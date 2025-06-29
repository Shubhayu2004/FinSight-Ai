from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ReportType(Enum):
    """Types of financial reports"""
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    DIRECTORS_REPORT = "directors_report"
    AUDITORS_REPORT = "auditors_report"
    PROSPECTUS = "prospectus"
    OTHER = "other"

class DocumentFormat(Enum):
    """Document formats"""
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    XLSX = "xlsx"

@dataclass
class AnnualReport:
    """Annual report data model"""
    symbol: str
    company_name: str
    report_type: ReportType
    year: int
    title: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    format: DocumentFormat = DocumentFormat.PDF
    download_date: Optional[datetime] = None
    filing_date: Optional[datetime] = None
    pages: Optional[int] = None
    extracted_text: Optional[str] = None
    sections: Optional[Dict[str, str]] = None
    metadata: Optional[Dict] = None

@dataclass
class ReportSection:
    """Section within a financial report"""
    name: str
    content: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    confidence: float = 1.0

@dataclass
class ReportExtractionResult:
    """Result of report extraction process"""
    success: bool
    report: Optional[AnnualReport] = None
    error_message: Optional[str] = None
    extraction_time: Optional[float] = None
    sections_found: Optional[List[str]] = None

@dataclass
class ReportSearchResult:
    """Result of searching for reports"""
    symbol: str
    reports: List[AnnualReport]
    total_count: int
    search_time: float
    sources_checked: List[str] 