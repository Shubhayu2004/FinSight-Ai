import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
from ..models import Company

class NSEScraper:
    """Scraper for NSE (National Stock Exchange) data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://www.nseindia.com"
    
    def get_all_companies(self) -> List[Company]:
        """Fetch all listed companies from NSE"""
        try:
            # NSE equity list URL
            url = f"{self.base_url}/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            companies = []
            
            for item in data.get('data', []):
                company = Company(
                    symbol=item.get('symbol', ''),
                    name=item.get('symbol', ''),  # NSE uses symbol as name
                    full_name=item.get('symbol', ''),
                    sector=item.get('sector', ''),
                    exchange='NSE',
                    last_updated=datetime.now()
                )
                companies.append(company)
            
            logging.info(f"Fetched {len(companies)} companies from NSE")
            return companies
            
        except Exception as e:
            logging.error(f"Error fetching NSE companies: {e}")
            return []
    
    def get_company_details(self, symbol: str) -> Optional[Company]:
        """Get detailed information for a specific company"""
        try:
            # NSE company details URL
            url = f"{self.base_url}/get-quotes/equity?symbol={symbol}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the response to extract company details
            # This is a simplified version - actual implementation would parse the HTML/JSON
            company = Company(
                symbol=symbol,
                name=symbol,
                full_name=symbol,
                exchange='NSE',
                last_updated=datetime.now()
            )
            
            return company
            
        except Exception as e:
            logging.error(f"Error fetching NSE company details for {symbol}: {e}")
            return None
    
    def search_companies(self, query: str) -> List[Company]:
        """Search companies by name or symbol"""
        try:
            # NSE search API
            url = f"{self.base_url}/api/search/autocomplete?q={query}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            companies = []
            
            for item in data.get('symbols', []):
                company = Company(
                    symbol=item.get('symbol', ''),
                    name=item.get('symbol', ''),
                    full_name=item.get('symbol', ''),
                    exchange='NSE',
                    last_updated=datetime.now()
                )
                companies.append(company)
            
            return companies
            
        except Exception as e:
            logging.error(f"Error searching NSE companies: {e}")
            return []

# Global instance
nse_scraper = NSEScraper() 