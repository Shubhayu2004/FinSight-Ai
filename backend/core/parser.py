import os
import pdfplumber
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
from typing import Optional, List
import logging

class DocumentParser:
    def __init__(self):
        self.supported_extensions = ['.pdf', '.html', '.htm']
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from a file based on its extension"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['.html', '.htm']:
            return self._extract_from_html(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def extract_text_from_url(self, url: str) -> str:
        """Extract text from a URL (HTML content)"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if it's a PDF URL
            if url.lower().endswith('.pdf'):
                # Download and parse PDF
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name
                
                try:
                    text = self._extract_from_pdf(tmp_file_path)
                finally:
                    os.unlink(tmp_file_path)
                return text
            else:
                # Parse as HTML
                return self._extract_from_html_content(response.text)
                
        except Exception as e:
            logging.error(f"Error extracting text from URL {url}: {e}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        text = ""
        
        # Try pdfplumber first (better for tables and structured content)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                return text.strip()
                
        except Exception as e:
            logging.warning(f"pdfplumber failed: {e}")
        
        # Fallback to PyMuPDF
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
            
            return text.strip()
            
        except Exception as e:
            logging.error(f"PyMuPDF failed: {e}")
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    def _extract_from_html(self, file_path: str) -> str:
        """Extract text from HTML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return self._extract_from_html_content(html_content)
    
    def _extract_from_html_content(self, html_content: str) -> str:
        """Extract text from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_sections(self, text: str, section_keywords: List[str] = None) -> dict:
        """Extract specific sections from annual report text"""
        if section_keywords is None:
            section_keywords = [
                "risk factors", "management discussion", "financial statements",
                "directors' report", "auditor's report", "corporate governance"
            ]
        
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line starts a new section
            for keyword in section_keywords:
                if keyword in line_lower and len(line.strip()) < 100:  # Likely a header
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = keyword
                    current_content = []
                    break
            else:
                if current_section:
                    current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

# Global instance
document_parser = DocumentParser() 