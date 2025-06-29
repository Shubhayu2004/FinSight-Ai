import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging

class AnnualReportScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_latest_annual_report_url(self, symbol: str) -> str:
        """Fetch the latest annual report URL for a given symbol"""
        # Try multiple sources in order of preference
        sources = [
            self._try_nse_website,
            self._try_bse_website,
            self._try_company_website,
            self._try_generic_search
        ]
        
        for source_func in sources:
            try:
                url = source_func(symbol)
                if url:
                    return url
            except Exception as e:
                logging.warning(f"Source {source_func.__name__} failed for {symbol}: {e}")
                continue
        
        # Fallback: return a placeholder URL
        return f"https://example.com/annual-reports/{symbol.lower()}-latest.pdf"
    
    def _try_nse_website(self, symbol: str) -> Optional[str]:
        """Try to find annual report on NSE website"""
        try:
            # NSE annual reports URL pattern
            nse_url = f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
            
            # This is a simplified approach - in production you'd need to handle NSE's dynamic content
            # For now, return a placeholder
            return f"https://www.nseindia.com/companies-listing/annual-reports/{symbol}"
            
        except Exception as e:
            logging.error(f"Error accessing NSE website: {e}")
            return None
    
    def _try_bse_website(self, symbol: str) -> Optional[str]:
        """Try to find annual report on BSE website"""
        try:
            # BSE annual reports URL pattern
            bse_url = f"https://www.bseindia.com/stock-share-price/{symbol}"
            
            # This is a simplified approach - in production you'd need to handle BSE's dynamic content
            return f"https://www.bseindia.com/stock-share-price/{symbol}/annual-reports"
            
        except Exception as e:
            logging.error(f"Error accessing BSE website: {e}")
            return None
    
    def _try_company_website(self, symbol: str) -> Optional[str]:
        """Try to find annual report on company's own website"""
        try:
            # Common company website patterns
            company_patterns = [
                f"https://www.{symbol.lower()}.com/investors/annual-reports",
                f"https://{symbol.lower()}.com/investor-relations/annual-reports",
                f"https://www.{symbol.lower()}.in/investors/annual-reports",
                f"https://{symbol.lower()}.in/investor-relations/annual-reports"
            ]
            
            for pattern in company_patterns:
                try:
                    response = self.session.get(pattern, timeout=10)
                    if response.status_code == 200:
                        # Check if page contains annual report links
                        soup = BeautifulSoup(response.text, 'html.parser')
                        if self._contains_annual_report_links(soup):
                            return pattern
                except:
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Error accessing company website: {e}")
            return None
    
    def _try_generic_search(self, symbol: str) -> Optional[str]:
        """Generic search for annual reports"""
        try:
            # Search for annual reports using common patterns
            search_terms = [
                f"{symbol} annual report 2024",
                f"{symbol} annual report 2023",
                f"{symbol} financial statements"
            ]
            
            # This would typically involve a search API or web scraping
            # For now, return a placeholder
            return f"https://search.example.com/annual-reports/{symbol}"
            
        except Exception as e:
            logging.error(f"Error in generic search: {e}")
            return None
    
    def _contains_annual_report_links(self, soup: BeautifulSoup) -> bool:
        """Check if a page contains annual report links"""
        text = soup.get_text().lower()
        annual_report_keywords = [
            'annual report', 'financial report', 'annual report 2024',
            'annual report 2023', 'financial statements', 'investor relations'
        ]
        
        return any(keyword in text for keyword in annual_report_keywords)
    
    def download_report(self, url: str, save_path: str) -> bool:
        """Download a report from URL"""
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            logging.error(f"Error downloading report from {url}: {e}")
            return False

# Global instance
annual_report_scraper = AnnualReportScraper()

# Backward compatibility function
def fetch_latest_annual_report_url(symbol: str) -> str:
    return annual_report_scraper.fetch_latest_annual_report_url(symbol) 