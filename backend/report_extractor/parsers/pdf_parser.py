import pdfplumber
import fitz  # PyMuPDF
from typing import List, Optional, Dict, Tuple
import logging
import re
from ..models import AnnualReport, ReportSection, DocumentFormat

class PDFParser:
    """Parser for PDF annual reports"""
    
    def __init__(self):
        self.section_keywords = {
            'management_discussion': [
                'management discussion', 'md&a', 'management discussion and analysis',
                'directors report', 'board report', 'management report'
            ],
            'financial_statements': [
                'financial statements', 'balance sheet', 'profit and loss',
                'income statement', 'cash flow', 'audited financials'
            ],
            'risk_factors': [
                'risk factors', 'risk management', 'risks and concerns',
                'business risks', 'operational risks'
            ],
            'corporate_governance': [
                'corporate governance', 'board of directors', 'directors',
                'governance report', 'board composition'
            ],
            'auditors_report': [
                'auditors report', 'audit report', 'independent auditors',
                'audit opinion', 'auditors certificate'
            ],
            'business_overview': [
                'business overview', 'company overview', 'about the company',
                'business description', 'company profile'
            ]
        }
    
    def parse_pdf(self, file_path: str) -> Tuple[str, List[ReportSection]]:
        """Parse PDF and extract text with sections"""
        try:
            # Extract full text
            full_text = self._extract_text(file_path)
            
            # Identify sections
            sections = self._identify_sections(full_text)
            
            return full_text, sections
            
        except Exception as e:
            logging.error(f"Error parsing PDF {file_path}: {e}")
            return "", []
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        text = ""
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logging.warning(f"pdfplumber failed, trying PyMuPDF: {e}")
            text = self._extract_text_pymupdf(file_path)
        
        return text
    
    def _extract_text_pymupdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF as fallback"""
        text = ""
        
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
        except Exception as e:
            logging.error(f"PyMuPDF extraction failed: {e}")
        
        return text
    
    def _identify_sections(self, text: str) -> List[ReportSection]:
        """Identify sections in the text"""
        sections = []
        lines = text.split('\n')
        
        for section_name, keywords in self.section_keywords.items():
            section_content = self._find_section_content(lines, keywords)
            if section_content:
                section = ReportSection(
                    name=section_name,
                    content=section_content,
                    confidence=0.8
                )
                sections.append(section)
        
        return sections
    
    def _find_section_content(self, lines: List[str], keywords: List[str]) -> Optional[str]:
        """Find content for a specific section based on keywords"""
        content_lines = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line starts a section
            if not in_section:
                for keyword in keywords:
                    if keyword in line_lower and len(line_lower) < 100:  # Likely a header
                        in_section = True
                        break
            
            # If in section, collect content
            elif in_section:
                # Check if we've reached another major section
                if self._is_major_section_header(line_lower):
                    break
                
                content_lines.append(line)
        
        if content_lines:
            return '\n'.join(content_lines)
        
        return None
    
    def _is_major_section_header(self, line: str) -> bool:
        """Check if line is a major section header"""
        # Look for all caps, numbered sections, or common headers
        if len(line) < 50 and (
            line.isupper() or
            re.match(r'^\d+\.', line) or
            re.match(r'^[A-Z][A-Z\s]+$', line)
        ):
            return True
        
        return False
    
    def extract_tables(self, file_path: str) -> List[Dict]:
        """Extract tables from PDF"""
        tables = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        if table and len(table) > 1:  # At least header + data
                            tables.append({
                                'page': page_num + 1,
                                'data': table
                            })
        except Exception as e:
            logging.error(f"Error extracting tables: {e}")
        
        return tables
    
    def get_page_count(self, file_path: str) -> int:
        """Get total number of pages in PDF"""
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            logging.error(f"Error getting page count: {e}")
            return 0
    
    def extract_metadata(self, file_path: str) -> Dict:
        """Extract PDF metadata"""
        metadata = {}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                if pdf.metadata:
                    metadata = pdf.metadata
        except Exception as e:
            logging.error(f"Error extracting metadata: {e}")
        
        return metadata

# Global instance
pdf_parser = PDFParser() 