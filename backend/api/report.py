from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict
import os
import tempfile
from core.parser import document_parser
from core.scraper import fetch_latest_annual_report_url

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

@router.post("/fetch-latest")
def fetch_latest_report(symbol: str = Form(...)):
    """Fetch the latest annual report for a company"""
    try:
        # Get the URL for the latest report
        report_url = fetch_latest_annual_report_url(symbol)
        
        # Extract text from the URL
        text = document_parser.extract_text_from_url(report_url)
        
        # Extract sections
        sections = document_parser.extract_sections(text)
        
        return {
            "symbol": symbol,
            "url": report_url,
            "text_length": len(text),
            "sections": list(sections.keys()),
            "full_text": text[:1000] + "..." if len(text) > 1000 else text  # Truncate for response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")

@router.post("/upload")
def upload_report(file: UploadFile = File(...), symbol: Optional[str] = Form(None)):
    """Upload and parse an annual report file"""
    try:
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in document_parser.supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported: {document_parser.supported_extensions}"
            )
        
        # Save uploaded file
        file_path = os.path.join(UPLOADS_DIR, f"{symbol}_{file.filename}" if symbol else file.filename)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Extract text from file
        text = document_parser.extract_text_from_file(file_path)
        
        # Extract sections
        sections = document_parser.extract_sections(text)
        
        return {
            "filename": file.filename,
            "symbol": symbol,
            "file_path": file_path,
            "text_length": len(text),
            "sections": list(sections.keys()),
            "full_text": text[:1000] + "..." if len(text) > 1000 else text  # Truncate for response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/parse-url")
def parse_url(url: str):
    """Parse text from a URL"""
    try:
        text = document_parser.extract_text_from_url(url)
        sections = document_parser.extract_sections(text)
        
        return {
            "url": url,
            "text_length": len(text),
            "sections": list(sections.keys()),
            "full_text": text[:1000] + "..." if len(text) > 1000 else text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing URL: {str(e)}") 