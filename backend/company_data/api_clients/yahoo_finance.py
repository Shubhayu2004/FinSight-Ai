import requests
from typing import List, Optional, Dict
import logging
from ..models import Company, CompanyMetadata

class YahooFinanceClient:
    """Client for Yahoo Finance API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://query1.finance.yahoo.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_companies(self, query: str) -> List[Company]:
        """Search companies using Yahoo Finance"""
        try:
            # Yahoo Finance search endpoint
            url = f"{self.base_url}/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': 20,
                'newsCount': 0
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            companies = []
            
            for quote in data.get('quotes', []):
                company = Company(
                    symbol=quote.get('symbol', ''),
                    name=quote.get('shortname', ''),
                    full_name=quote.get('longname', ''),
                    sector=quote.get('sector', ''),
                    industry=quote.get('industry', ''),
                    market_cap=quote.get('marketcap'),
                    exchange=quote.get('exchange', ''),
                    last_updated=datetime.now()
                )
                companies.append(company)
            
            return companies
            
        except Exception as e:
            logging.error(f"Error searching Yahoo Finance: {e}")
            return []
    
    def get_company_details(self, symbol: str) -> Optional[Company]:
        """Get detailed company information"""
        try:
            # Yahoo Finance quote endpoint
            url = f"{self.base_url}/v8/finance/chart/{symbol}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            result = data.get('chart', {}).get('result', [{}])[0]
            meta = result.get('meta', {})
            
            company = Company(
                symbol=symbol,
                name=meta.get('shortName', symbol),
                full_name=meta.get('longName', symbol),
                sector=meta.get('sector', ''),
                industry=meta.get('industry', ''),
                market_cap=meta.get('marketCap'),
                exchange=meta.get('exchangeName', ''),
                last_updated=datetime.now()
            )
            
            return company
            
        except Exception as e:
            logging.error(f"Error fetching Yahoo Finance details for {symbol}: {e}")
            return None
    
    def get_company_metadata(self, symbol: str) -> Optional[CompanyMetadata]:
        """Get additional company metadata"""
        try:
            # Yahoo Finance company profile endpoint
            url = f"{self.base_url}/v10/finance/quoteSummary/{symbol}"
            params = {
                'modules': 'assetProfile,summaryDetail'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            result = data.get('quoteSummary', {}).get('result', [{}])[0]
            
            asset_profile = result.get('assetProfile', {})
            summary_detail = result.get('summaryDetail', {})
            
            metadata = CompanyMetadata(
                company_id=symbol,
                website=asset_profile.get('website'),
                description=asset_profile.get('longBusinessSummary'),
                employees=asset_profile.get('fullTimeEmployees'),
                headquarters=asset_profile.get('city') + ', ' + asset_profile.get('country') if asset_profile.get('city') else None
            )
            
            return metadata
            
        except Exception as e:
            logging.error(f"Error fetching Yahoo Finance metadata for {symbol}: {e}")
            return None

# Global instance
yahoo_finance_client = YahooFinanceClient() 