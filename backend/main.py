from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
import traceback
from pathlib import Path
import sys

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import REPORTS_DIR, UPLOAD_DIR, CACHE_DIR, setup_model_cache
from annual_report_processor import AnnualReportProcessor
from annual_report_processor.llm_client import FinGPTLLMClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup model cache
setup_model_cache()

# Initialize FastAPI app
app = FastAPI(
    title="AI Finance Agent API",
    description="Financial analysis API using FinGPT model for annual report analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the processor with FinGPT model
try:
    processor = AnnualReportProcessor(
        llm_client_type="fingpt",
        max_context_tokens=4000,
        cache_dir=str(CACHE_DIR)
    )
    logger.info("✅ Annual Report Processor initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize processor: {e}")
    processor = None

# Pydantic models
class QueryRequest(BaseModel):
    pdf_filename: str
    query: str
    company_name: Optional[str] = None
    force_reprocess: bool = False

class ProcessRequest(BaseModel):
    pdf_filename: str
    force_reprocess: bool = False

class ModelInfoResponse(BaseModel):
    model_name: str
    model_type: str
    device: str
    cuda_available: bool
    parameters: str
    description: str
    uses_peft: bool

class HealthResponse(BaseModel):
    status: str
    model_available: bool
    processor_available: bool
    cache_directory: str
    upload_directory: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health of the API and model."""
    return HealthResponse(
        status="healthy",
        model_available=processor.llm_client.is_available() if processor else False,
        processor_available=processor is not None,
        cache_directory=str(CACHE_DIR),
        upload_directory=str(UPLOAD_DIR)
    )

# Model information endpoint
@app.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the loaded FinGPT model."""
    try:
        if processor and processor.llm_client.is_available():
            model_info = processor.llm_client.get_model_info()
            return ModelInfoResponse(**model_info)
        else:
            raise HTTPException(status_code=503, detail="Model not available")
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

# Test model endpoint
@app.post("/test-model")
async def test_model():
    """Test the FinGPT model with a simple query."""
    try:
        if not processor or not processor.llm_client.is_available():
            raise HTTPException(status_code=503, detail="Model not available")
        
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
        logger.error(f"Error testing model: {e}")
        return {
            "success": False,
            "test_query": "Test query",
            "response": f"Error: {str(e)}",
            "model_available": processor.llm_client.is_available() if processor else False
        }

# File upload endpoint
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for processing."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save file to uploads directory
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

# Process report endpoint
@app.post("/process-report")
async def process_report(request: ProcessRequest):
    """Process an uploaded PDF file."""
    try:
        if not processor:
            raise HTTPException(status_code=503, detail="Processor not available")
        
        pdf_path = UPLOAD_DIR / request.pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Process the report
        result = processor.process_annual_report(str(pdf_path), request.force_reprocess)
        
        # Count sections found
        sections_found = {}
        for section_type, sections in result['parsed_data']['sections'].items():
            sections_found[section_type] = len(sections)
        
        return {
            "success": True,
            "file_name": result['file_name'],
            "total_chunks": result['total_chunks'],
            "sections_found": sections_found,
            "financial_data": result['parsed_data']['financial_data']
        }
        
    except Exception as e:
        logger.error(f"Error processing report: {e}")
        return {
            "success": False,
            "file_name": request.pdf_filename,
            "total_chunks": 0,
            "sections_found": {},
            "financial_data": {},
            "error": str(e)
        }

# Query report endpoint
@app.post("/query-report")
async def query_report(request: QueryRequest):
    """Query the FinGPT model about a processed annual report."""
    try:
        if not processor:
            raise HTTPException(status_code=503, detail="Processor not available")
        
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
        
        return {
            "success": result['success'],
            "query": result['query'],
            "response": result['response'],
            "pdf_file": result['pdf_file'],
            "company_name": result['company_name'],
            "context_tokens": result.get('context_tokens', 0),
            "total_chunks_available": result.get('total_chunks_available', 0),
            "error": result.get('error')
        }
        
    except Exception as e:
        logger.error(f"Error querying report: {e}")
        return {
            "success": False,
            "query": request.query,
            "response": f"Error: {str(e)}",
            "pdf_file": request.pdf_filename,
            "company_name": request.company_name or "Unknown",
            "context_tokens": 0,
            "total_chunks_available": 0,
            "error": str(e)
        }

# Get available sections endpoint
@app.get("/available-sections/{pdf_filename}")
async def get_available_sections(pdf_filename: str):
    """Get available sections in a processed annual report."""
    try:
        if not processor:
            raise HTTPException(status_code=503, detail="Processor not available")
        
        pdf_path = UPLOAD_DIR / pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        sections = processor.get_available_sections(str(pdf_path))
        return sections
        
    except Exception as e:
        logger.error(f"Error getting sections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get financial summary endpoint
@app.get("/financial-summary/{pdf_filename}")
async def get_financial_summary(pdf_filename: str):
    """Get financial summary from a processed annual report."""
    try:
        if not processor:
            raise HTTPException(status_code=503, detail="Processor not available")
        
        pdf_path = UPLOAD_DIR / pdf_filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        processed_data = processor.process_annual_report(str(pdf_path))
        return processed_data['parsed_data']['financial_data']
        
    except Exception as e:
        logger.error(f"Error getting financial summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation history endpoints
@app.get("/conversation-history")
async def get_conversation_history():
    """Get conversation history."""
    try:
        if not processor:
            return []
        return processor.finagent.get_conversation_history()
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return []

@app.delete("/conversation-history")
async def clear_conversation_history():
    """Clear conversation history."""
    try:
        if processor:
            processor.finagent.clear_history()
        return {"message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File management endpoints
@app.get("/uploaded-files")
async def get_uploaded_files():
    """Get list of uploaded PDF files."""
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*.pdf"):
            files.append(file_path.name)
        return files
    except Exception as e:
        logger.error(f"Error getting uploaded files: {e}")
        return []

@app.delete("/uploaded-files/{pdf_filename}")
async def delete_uploaded_file(pdf_filename: str):
    """Delete an uploaded PDF file."""
    try:
        file_path = UPLOAD_DIR / pdf_filename
        if file_path.exists():
            file_path.unlink()
            return {"message": f"File {pdf_filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# View PDF endpoint
@app.get("/view-pdf/{pdf_filename}")
async def view_pdf(pdf_filename: str):
    """View an uploaded PDF file."""
    try:
        file_path = UPLOAD_DIR / pdf_filename
        if file_path.exists():
            return FileResponse(
                file_path, 
                media_type="application/pdf", 
                filename=pdf_filename
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error viewing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Finance Agent API is running",
        "version": "1.0.0",
        "model_available": processor.llm_client.is_available() if processor else False,
        "endpoints": {
            "health": "/health",
            "model_info": "/model-info",
            "test_model": "/test-model",
            "upload_pdf": "/upload-pdf",
            "process_report": "/process-report",
            "query_report": "/query-report",
            "available_sections": "/available-sections/{pdf_filename}",
            "financial_summary": "/financial-summary/{pdf_filename}",
            "conversation_history": "/conversation-history",
            "uploaded_files": "/uploaded-files"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 