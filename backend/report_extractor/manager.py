import os
import time
from typing import List, Optional, Dict
import logging
from datetime import datetime
import re

from .models import AnnualReport, ReportExtractionResult, ReportSearchResult, ReportType, DocumentFormat
from .scrapers.company_website_scraper import company_website_scraper
from .parsers.pdf_parser import pdf_parser

class ReportExtractionManager:
    """Manager for extracting annual reports from various sources"""
    
    def __init__(self, download_dir: str = "../Company Annual report"):
        self.download_dir = download_dir
        self.ensure_download_dir()
    
    def ensure_download_dir(self):
        """Ensure download directory exists"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logging.info(f"Created download directory: {self.download_dir}")
    
    def find_latest_annual_report(self, symbol: str, company_name: str) -> ReportSearchResult:
        """Find the latest annual report for a company"""
        import time
        start_time = time.time()
        sources_checked = []
        
        reports = []
        
        # Try company website first
        try:
            sources_checked.append("company_website")
            website_reports = company_website_scraper.find_annual_reports(symbol, company_name)
            reports.extend(website_reports)
        except Exception as e:
            logging.warning(f"Company website scraping failed: {e}")
        
        # Sort by year (latest first)
        reports.sort(key=lambda x: x.year, reverse=True)
        
        search_time = time.time() - start_time
        
        return ReportSearchResult(
            symbol=symbol,
            reports=reports,
            total_count=len(reports),
            search_time=search_time,
            sources_checked=sources_checked
        )
    
    def download_and_parse_report(self, report: AnnualReport) -> ReportExtractionResult:
        """Download and parse a report"""
        import time
        start_time = time.time()
        
        try:
            # Download report
            if report.url and not report.file_path:
                success = company_website_scraper.download_report(report, self.download_dir)
                if not success:
                    return ReportExtractionResult(
                        success=False,
                        error_message="Failed to download report"
                    )
            
            # Parse report
            if report.file_path and os.path.exists(report.file_path):
                if report.format == DocumentFormat.PDF:
                    full_text, sections = pdf_parser.parse_pdf(report.file_path)
                    
                    # Update report with extracted content
                    report.extracted_text = full_text
                    report.sections = {section.name: section.content for section in sections}
                    report.pages = pdf_parser.get_page_count(report.file_path)
                    report.metadata = pdf_parser.extract_metadata(report.file_path)
                    
                    extraction_time = time.time() - start_time
                    
                    return ReportExtractionResult(
                        success=True,
                        report=report,
                        extraction_time=extraction_time,
                        sections_found=list(report.sections.keys()) if report.sections else []
                    )
                else:
                    return ReportExtractionResult(
                        success=False,
                        error_message=f"Unsupported format: {report.format}"
                    )
            else:
                return ReportExtractionResult(
                    success=False,
                    error_message="Report file not found"
                )
                
        except Exception as e:
            logging.error(f"Error processing report: {e}")
            return ReportExtractionResult(
                success=False,
                error_message=str(e)
            )
    
    def get_latest_report_for_company(self, symbol: str, company_name: str) -> Optional[AnnualReport]:
        """Get the latest annual report for a company, downloading if necessary"""
        # First check if we already have a recent report
        existing_report = self._find_existing_report(symbol)
        if existing_report:
            return existing_report
        
        # Search for new reports
        search_result = self.find_latest_annual_report(symbol, company_name)
        
        if search_result.reports:
            latest_report = search_result.reports[0]
            
            # Download and parse
            extraction_result = self.download_and_parse_report(latest_report)
            
            if extraction_result.success:
                return extraction_result.report
        
        return None
    
    def _find_existing_report(self, symbol: str) -> Optional[AnnualReport]:
        """Find existing report in download directory"""
        try:
            for filename in os.listdir(self.download_dir):
                if filename.startswith(symbol) and filename.endswith('.pdf'):
                    file_path = os.path.join(self.download_dir, filename)
                    
                    # Extract year from filename
                    year_match = re.search(r'_(\d{4})_', filename)
                    year = int(year_match.group(1)) if year_match else datetime.now().year
                    
                    # Check if file is recent (within last 2 years)
                    if year >= datetime.now().year - 2:
                        report = AnnualReport(
                            symbol=symbol,
                            company_name=symbol,  # Will be updated if needed
                            report_type=ReportType.ANNUAL_REPORT,
                            year=year,
                            title=f"Annual Report {year}",
                            file_path=file_path,
                            format=DocumentFormat.PDF,
                            download_date=datetime.fromtimestamp(os.path.getctime(file_path))
                        )
                        
                        # Parse if not already parsed
                        if not report.extracted_text:
                            extraction_result = self.download_and_parse_report(report)
                            if extraction_result.success:
                                return extraction_result.report
                        
                        return report
        except Exception as e:
            logging.error(f"Error finding existing report: {e}")
        
        return None
    
    def get_report_sections(self, report: AnnualReport, section_names: List[str] = None) -> Dict[str, str]:
        """Get specific sections from a report"""
        if not report.sections:
            # Parse report if not already parsed
            extraction_result = self.download_and_parse_report(report)
            if not extraction_result.success:
                return {}
        
        if section_names:
            return {name: report.sections.get(name, '') for name in section_names}
        else:
            return report.sections or {}
    
    def search_reports_by_content(self, symbol: str, search_terms: List[str]) -> List[str]:
        """Search for specific content within a company's reports"""
        report = self.get_latest_report_for_company(symbol, symbol)
        
        if not report or not report.extracted_text:
            return []
        
        matching_sections = []
        text_lower = report.extracted_text.lower()
        
        for term in search_terms:
            if term.lower() in text_lower:
                # Find which section contains this term
                for section_name, section_content in report.sections.items():
                    if term.lower() in section_content.lower():
                        matching_sections.append(section_name)
        
        return list(set(matching_sections))

# Global instance
report_manager = ReportExtractionManager() 