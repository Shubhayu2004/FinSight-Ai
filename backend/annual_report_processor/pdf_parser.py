import fitz  # PyMuPDF
import re
import os
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """PDF parser for annual reports with section extraction capabilities."""
    
    def __init__(self):
        # Common section headers in annual reports
        self.section_keywords = {
            'financial_statements': [
                'financial statements', 'consolidated financial statements', 
                'standalone financial statements', 'balance sheet', 'profit and loss',
                'cash flow statement', 'notes to accounts'
            ],
            'management_discussion': [
                'management discussion and analysis', 'mda', 'directors\' report',
                'management commentary', 'ceo message', 'chairman\'s statement'
            ],
            'risk_factors': [
                'risk factors', 'risk management', 'risks and concerns',
                'business risks', 'operational risks'
            ],
            'esg': [
                'environmental', 'social', 'governance', 'esg', 'sustainability',
                'corporate social responsibility', 'csr'
            ],
            'business_overview': [
                'business overview', 'company overview', 'about us',
                'business model', 'operational review'
            ],
            'corporate_governance': [
                'corporate governance', 'board of directors', 'board report',
                'governance report'
            ]
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
                text += "\n"  # Add page break
            
            doc.close()
            logger.info(f"Successfully extracted text from {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\b\d+\s*of\s*\d+\b', '', text)  # "Page X of Y"
        text = re.sub(r'\bPage\s+\d+\b', '', text)      # "Page X"
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\%\$\€\₹]', '', text)
        
        return text.strip()
    
    def find_sections(self, text: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """Find sections in the text based on keywords."""
        sections = {key: [] for key in self.section_keywords.keys()}
        
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            for section_type, keywords in self.section_keywords.items():
                for keyword in keywords:
                    if keyword in line_lower:
                        # Find the end of this section (next major heading)
                        end_line = self._find_section_end(lines, line_num)
                        section_text = '\n'.join(lines[line_num:end_line])
                        
                        sections[section_type].append((line_num, end_line, section_text))
                        break
        
        return sections
    
    def _find_section_end(self, lines: List[str], start_line: int) -> int:
        """Find the end of a section by looking for the next major heading."""
        # Look for common heading patterns
        heading_patterns = [
            r'^\d+\.\s+[A-Z]',  # "1. SECTION"
            r'^[A-Z][A-Z\s]{3,}$',  # "ALL CAPS HEADING"
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # "Title Case Heading"
        ]
        
        for line_num in range(start_line + 1, len(lines)):
            line = lines[line_num].strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this line matches a heading pattern
            for pattern in heading_patterns:
                if re.match(pattern, line):
                    return line_num
            
            # If we've gone too far without finding a heading, stop
            if line_num > start_line + 50:  # Max 50 lines per section
                return line_num
        
        return len(lines)
    
    def extract_financial_data(self, text: str) -> Dict[str, str]:
        """Extract key financial metrics using regex patterns."""
        financial_data = {}
        
        # Revenue patterns
        revenue_patterns = [
            r'revenue[:\s]*₹?\s*([\d,]+\.?\d*)',
            r'total\s+revenue[:\s]*₹?\s*([\d,]+\.?\d*)',
            r'sales[:\s]*₹?\s*([\d,]+\.?\d*)'
        ]
        
        # Net Profit patterns
        profit_patterns = [
            r'net\s+profit[:\s]*₹?\s*([\d,]+\.?\d*)',
            r'profit\s+after\s+tax[:\s]*₹?\s*([\d,]+\.?\d*)',
            r'pat[:\s]*₹?\s*([\d,]+\.?\d*)'
        ]
        
        # EPS patterns
        eps_patterns = [
            r'earnings\s+per\s+share[:\s]*₹?\s*([\d,]+\.?\d*)',
            r'eps[:\s]*₹?\s*([\d,]+\.?\d*)'
        ]
        
        # Extract values
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                financial_data['revenue'] = match.group(1)
                break
        
        for pattern in profit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                financial_data['net_profit'] = match.group(1)
                break
        
        for pattern in eps_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                financial_data['eps'] = match.group(1)
                break
        
        return financial_data
    
    def parse_annual_report(self, pdf_path: str) -> Dict[str, any]:
        """Main method to parse an annual report PDF."""
        logger.info(f"Starting to parse {pdf_path}")
        
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        cleaned_text = self.clean_text(raw_text)
        
        # Find sections
        sections = self.find_sections(cleaned_text)
        
        # Extract financial data
        financial_data = self.extract_financial_data(cleaned_text)
        
        # Compile results
        result = {
            'file_path': pdf_path,
            'file_name': os.path.basename(pdf_path),
            'total_text_length': len(cleaned_text),
            'sections': sections,
            'financial_data': financial_data,
            'full_text': cleaned_text
        }
        
        logger.info(f"Successfully parsed {pdf_path}")
        logger.info(f"Found {len(sections)} section types")
        logger.info(f"Extracted {len(financial_data)} financial metrics")
        
        return result

# Example usage
if __name__ == "__main__":
    parser = PDFParser()
    # result = parser.parse_annual_report("path/to/annual_report.pdf")
    # print(result) 