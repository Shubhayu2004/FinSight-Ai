from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from pathlib import Path

# Import the annual report processor
from annual_report_processor import AnnualReportProcessor

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Annual Report Analysis API", version="1.0.0")

# Initialize the processor with FinAgent model
processor = AnnualReportProcessor(
    llm_client_type="finagent",  # Use the fine-tuned FinAgent model
    max_context_tokens=4000
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    pdf_filename: str
    query: str
    company_name: Optional[str] = None
    force_reprocess: bool = False

class ProcessRequest(BaseModel):
    pdf_filename: str
    force_reprocess: bool = False

class BatchProcessRequest(BaseModel):
    force_reprocess: bool = False

class QueryResponse(BaseModel):
    success: bool
    query: str
    response: str
    pdf_file: str
    company_name: str
    context_tokens: int
    total_chunks_available: int
    error: Optional[str] = None

class ProcessResponse(BaseModel):
    success: bool
    file_name: str
    total_chunks: int
    sections_found: Dict[str, int]
    financial_data: Dict[str, str]
    error: Optional[str] = None

class StatsResponse(BaseModel):
    total_processed_files: int
    cache_directory: str
    llm_client_type: str
    llm_available: bool
    conversation_history_length: int

class ModelInfoResponse(BaseModel):
    model_path: str
    base_model: str
    adapter_type: str
    device: str
    parameters: int
    trainable_parameters: int
    status: str

@app.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the loaded FinAgent model."""
    try:
        if hasattr(processor.llm_client, 'get_model_info'):
            model_info = processor.llm_client.get_model_info()
            return ModelInfoResponse(**model_info)
        else:
            return ModelInfoResponse(
                model_path="N/A",
                base_model="N/A",
                adapter_type="N/A",
                device="N/A",
                parameters=0,
                trainable_parameters=0,
                status="No model info available"
            )
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@app.post("/test-finagent")
async def test_finagent():
    """Test the FinAgent model with a simple query."""
    try:
        test_context = "Revenue: ₹50,000 crores, Net Profit: ₹8,000 crores, EPS: ₹25.50"
        test_query = "What is the company's profit margin?"
        
        response = processor.finagent.query_annual_report(
            context=test_context,
            query=test_query,
            company_name="Test Company"
        )
        
        return {
            "success": response['success'],
            "test_query": test_query,
            "response": response['response'],
            "model_available": processor.llm_client.is_available()
        }
        
    except Exception as e:
        logger.error(f"Error testing FinAgent: {e}")
        return {
            "success": False,
            "test_query": "Test query",
            "response": f"Error: {str(e)}",
            "model_available": processor.llm_client.is_available()
        }

@app.post("/upload-pdf", response_model=Dict[str, str])
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for processing."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Uploaded PDF: {file.filename}")
        
        return {
            "message": "PDF uploaded successfully",
            "filename": file.filename,
            "file_path": str(file_path)
        }
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/process-report", response_model=ProcessResponse)
async def process_report(request: ProcessRequest):
    """Process an uploaded PDF file."""
    try:
        pdf_path = UPLOAD_DIR / request.pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Process the report
        result = processor.process_annual_report(str(pdf_path), request.force_reprocess)
        
        # Count sections found
        sections_found = {}
        for section_type, sections in result['parsed_data']['sections'].items():
            sections_found[section_type] = len(sections)
        
        return ProcessResponse(
            success=True,
            file_name=result['file_name'],
            total_chunks=result['total_chunks'],
            sections_found=sections_found,
            financial_data=result['parsed_data']['financial_data']
        )
        
    except Exception as e:
        logger.error(f"Error processing report: {e}")
        return ProcessResponse(
            success=False,
            file_name=request.pdf_filename,
            total_chunks=0,
            sections_found={},
            financial_data={},
            error=str(e)
        )

@app.post("/query-report", response_model=QueryResponse)
async def query_report(request: QueryRequest):
    """Query the FinAgent about a processed annual report."""
    try:
        pdf_path = UPLOAD_DIR / request.pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Query the report
        result = processor.query_annual_report(
            str(pdf_path),
            request.query,
            request.company_name,
            request.force_reprocess
        )
        
        return QueryResponse(
            success=result['success'],
            query=result['query'],
            response=result['response'],
            pdf_file=result['pdf_file'],
            company_name=result['company_name'],
            context_tokens=result['context_tokens'],
            total_chunks_available=result['total_chunks_available'],
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Error querying report: {e}")
        return QueryResponse(
            success=False,
            query=request.query,
            response="",
            pdf_file=request.pdf_filename,
            company_name=request.company_name or "Unknown",
            context_tokens=0,
            total_chunks_available=0,
            error=str(e)
        )

@app.post("/batch-process", response_model=List[ProcessResponse])
async def batch_process_reports(request: BatchProcessRequest):
    """Process all PDF files in the upload directory."""
    try:
        results = processor.batch_process_reports(str(UPLOAD_DIR))
        
        response_list = []
        for result in results:
            if result.get('success', True):
                sections_found = {}
                for section_type, sections in result['parsed_data']['sections'].items():
                    sections_found[section_type] = len(sections)
                
                response_list.append(ProcessResponse(
                    success=True,
                    file_name=result['file_name'],
                    total_chunks=result['total_chunks'],
                    sections_found=sections_found,
                    financial_data=result['parsed_data']['financial_data']
                ))
            else:
                response_list.append(ProcessResponse(
                    success=False,
                    file_name=result['file_name'],
                    total_chunks=0,
                    sections_found={},
                    financial_data={},
                    error=result.get('error', 'Unknown error')
                ))
        
        return response_list
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.get("/available-sections/{pdf_filename}", response_model=Dict[str, List[str]])
async def get_available_sections(pdf_filename: str):
    """Get available sections in a processed annual report."""
    try:
        pdf_path = UPLOAD_DIR / pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        sections = processor.get_available_sections(str(pdf_path))
        return sections
        
    except Exception as e:
        logger.error(f"Error getting sections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sections: {str(e)}")

@app.get("/financial-summary/{pdf_filename}", response_model=Dict[str, str])
async def get_financial_summary(pdf_filename: str):
    """Get financial summary from a processed annual report."""
    try:
        pdf_path = UPLOAD_DIR / pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        financial_data = processor.get_financial_summary(str(pdf_path))
        return financial_data
        
    except Exception as e:
        logger.error(f"Error getting financial summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get financial summary: {str(e)}")

@app.get("/conversation-history", response_model=List[Dict[str, Any]])
async def get_conversation_history():
    """Get the conversation history."""
    try:
        return processor.get_conversation_history()
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@app.delete("/conversation-history")
async def clear_conversation_history():
    """Clear the conversation history."""
    try:
        processor.clear_conversation_history()
        return {"message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation history: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_processing_stats():
    """Get processing statistics."""
    try:
        stats = processor.get_processing_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/uploaded-files", response_model=List[str])
async def get_uploaded_files():
    """Get list of uploaded PDF files."""
    try:
        pdf_files = [f.name for f in UPLOAD_DIR.glob("*.pdf")]
        return pdf_files
    except Exception as e:
        logger.error(f"Error getting uploaded files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get uploaded files: {str(e)}")

@app.delete("/uploaded-files/{pdf_filename}")
async def delete_uploaded_file(pdf_filename: str):
    """Delete an uploaded PDF file."""
    try:
        pdf_path = UPLOAD_DIR / pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        pdf_path.unlink()
        logger.info(f"Deleted PDF: {pdf_filename}")
        
        return {"message": f"File {pdf_filename} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_available": processor.llm_client.is_available(),
        "llm_type": type(processor.llm_client).__name__,
        "upload_directory": str(UPLOAD_DIR),
        "uploaded_files_count": len(list(UPLOAD_DIR.glob("*.pdf")))
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 