import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

from ..models import AnnualReport, ReportType, DocumentFormat

class CompanyWebsiteScraper:
    """Scraper for company websites to find annual reports"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_annual_reports(self, symbol: str, company_name: str) -> List[AnnualReport]:
        """Find annual reports on company website"""
        reports = []
        
        # Common website patterns for Indian companies
        website_patterns = [
            f"https://www.{symbol.lower()}.com",
            f"https://{symbol.lower()}.com",
            f"https://www.{symbol.lower()}.in",
            f"https://{symbol.lower()}.in",
            f"https://www.{company_name.lower().replace(' ', '').replace('.', '').replace('ltd', '').replace('limited', '')}.com",
        ]
        
        for base_url in website_patterns:
            try:
                company_reports = self._scrape_company_website(base_url, symbol, company_name)
                reports.extend(company_reports)
            except Exception as e:
                logging.warning(f"Failed to scrape {base_url}: {e}")
                continue
        
        return reports
    
    def _scrape_company_website(self, base_url: str, symbol: str, company_name: str) -> List[AnnualReport]:
        """Scrape a specific company website for annual reports"""
        reports = []
        
        # Common investor relations page patterns
        ir_patterns = [
            "/investors",
            "/investor-relations",
            "/investor",
            "/shareholders",
            "/annual-reports",
            "/financial-reports",
            "/reports",
        ]
        
        for pattern in ir_patterns:
            try:
                ir_url = urljoin(base_url, pattern)
                response = self.session.get(ir_url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    found_reports = self._extract_reports_from_page(soup, ir_url, symbol, company_name)
                    reports.extend(found_reports)
                    
                    if found_reports:
                        break  # Found reports, no need to check other patterns
                        
            except Exception as e:
                logging.debug(f"Failed to check {pattern} on {base_url}: {e}")
                continue
        
        return reports
    
    def _extract_reports_from_page(self, soup: BeautifulSoup, page_url: str, symbol: str, company_name: str) -> List[AnnualReport]:
        """Extract annual report links from a webpage"""
        reports = []
        
        # Look for links containing annual report keywords
        annual_report_keywords = [
            'annual report', 'annual report 2024', 'annual report 2023',
            'annual report 2022', 'annual report 2021', 'annual report 2020',
            'financial report', 'annual financial report', 'directors report'
        ]
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text().lower()
            href = link.get('href', '')
            
            # Check if link text contains annual report keywords
            for keyword in annual_report_keywords:
                if keyword in link_text:
                    report_url = urljoin(page_url, href)
                    
                    # Determine year from text
                    year = self._extract_year_from_text(link_text)
                    
                    # Determine file format
                    file_format = self._determine_file_format(report_url)
                    
                    if year and file_format:
                        report = AnnualReport(
                            symbol=symbol,
                            company_name=company_name,
                            report_type=ReportType.ANNUAL_REPORT,
                            year=year,
                            title=link.get_text().strip(),
                            url=report_url,
                            format=file_format,
                            download_date=datetime.now()
                        )
                        reports.append(report)
                        break
        
        return reports
    
    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract year from text"""
        # Look for 4-digit years
        year_pattern = r'\b(20[12]\d)\b'
        match = re.search(year_pattern, text)
        
        if match:
            return int(match.group(1))
        
        # Look for 2-digit years and convert
        year_pattern_2digit = r'\b(2[12])\b'
        match = re.search(year_pattern_2digit, text)
        
        if match:
            year_2digit = int(match.group(1))
            return 2000 + year_2digit
        
        return None
    
    def _determine_file_format(self, url: str) -> Optional[DocumentFormat]:
        """Determine file format from URL"""
        url_lower = url.lower()
        
        if url_lower.endswith('.pdf'):
            return DocumentFormat.PDF
        elif url_lower.endswith('.html') or url_lower.endswith('.htm'):
            return DocumentFormat.HTML
        elif url_lower.endswith('.docx'):
            return DocumentFormat.DOCX
        elif url_lower.endswith('.xlsx'):
            return DocumentFormat.XLSX
        
        return None
    
    def download_report(self, report: AnnualReport, save_dir: str) -> bool:
        """Download a report from URL"""
        try:
            if not report.url:
                return False
            
            response = self.session.get(report.url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Create filename
            filename = f"{report.symbol}_{report.year}_annual_report.{report.format.value}"
            file_path = f"{save_dir}/{filename}"
            
            # Save file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Update report with file path
            report.file_path = file_path
            report.file_size = len(response.content)
            
            return True
            
        except Exception as e:
            logging.error(f"Error downloading report {report.url}: {e}")
            return False

# Global instance
company_website_scraper = CompanyWebsiteScraper() 