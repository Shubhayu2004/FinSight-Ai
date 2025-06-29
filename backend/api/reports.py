from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging

from ..report_extractor.manager import report_manager
from ..report_extractor.models import AnnualReport, ReportExtractionResult, ReportSearchResult

router = APIRouter(prefix="/api/reports", tags=["Report Extraction"])

@router.post("/fetch/{symbol}")
async def fetch_latest_report(symbol: str) -> ReportExtractionResult:
    """Fetch the latest annual report for a company"""
    try:
        # Get company name (simplified - would get from company manager)
        company_name = symbol
        
        # Find and download latest report
        report = report_manager.get_latest_report_for_company(symbol, company_name)
        
        if not report:
            raise HTTPException(status_code=404, detail="No annual report found for this company")
        
        return ReportExtractionResult(
            success=True,
            report=report,
            extraction_time=0.0,
            sections_found=list(report.sections.keys()) if report.sections else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching report for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching annual report")

@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    symbol: str = Form(...),
    year: int = Form(...),
    company_name: str = Form(...)
):
    """Upload and parse an annual report file"""
    try:
        # Save uploaded file
        file_path = f"../Company Annual report/{symbol}_{year}_uploaded.{file.filename.split('.')[-1]}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create report object
        from ..report_extractor.models import ReportType, DocumentFormat
        
        report = AnnualReport(
            symbol=symbol,
            company_name=company_name,
            report_type=ReportType.ANNUAL_REPORT,
            year=year,
            title=f"Uploaded Annual Report {year}",
            file_path=file_path,
            format=DocumentFormat.PDF if file.filename.endswith('.pdf') else DocumentFormat.HTML
        )
        
        # Parse the report
        extraction_result = report_manager.download_and_parse_report(report)
        
        if not extraction_result.success:
            raise HTTPException(status_code=400, detail=extraction_result.error_message)
        
        return extraction_result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading report: {e}")
        raise HTTPException(status_code=500, detail="Error processing uploaded report")

@router.get("/{symbol}/latest")
async def get_latest_report(symbol: str) -> AnnualReport:
    """Get the latest annual report for a company"""
    try:
        # Get company name (simplified)
        company_name = symbol
        
        report = report_manager.get_latest_report_for_company(symbol, company_name)
        
        if not report:
            raise HTTPException(status_code=404, detail="No annual report found for this company")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting latest report for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving annual report")

@router.get("/{symbol}/sections")
async def get_report_sections(
    symbol: str,
    section_names: Optional[str] = None
):
    """Get specific sections from the latest report"""
    try:
        # Get company name (simplified)
        company_name = symbol
        
        report = report_manager.get_latest_report_for_company(symbol, company_name)
        
        if not report:
            raise HTTPException(status_code=404, detail="No annual report found for this company")
        
        # Parse section names if provided
        sections_to_get = None
        if section_names:
            sections_to_get = [s.strip() for s in section_names.split(',')]
        
        sections = report_manager.get_report_sections(report, sections_to_get)
        
        return {
            "symbol": symbol,
            "sections": sections,
            "available_sections": list(report.sections.keys()) if report.sections else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting report sections for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving report sections")

@router.get("/{symbol}/search")
async def search_report_content(
    symbol: str,
    terms: str
):
    """Search for specific content within the company's reports"""
    try:
        search_terms = [term.strip() for term in terms.split(',')]
        matching_sections = report_manager.search_reports_by_content(symbol, search_terms)
        
        return {
            "symbol": symbol,
            "search_terms": search_terms,
            "matching_sections": matching_sections
        }
        
    except Exception as e:
        logging.error(f"Error searching report content for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error searching report content") 