import pandas as pd
import os
from typing import List, Optional, Dict
from datetime import datetime
import logging

from .models import Company, CompanySearchResult, CompanyMetadata
from .scrapers.nse_scraper import nse_scraper
from .api_clients.yahoo_finance import yahoo_finance_client

class CompanyDataManager:
    """Manager for company data from multiple sources"""
    
    def __init__(self, csv_path: str = "ind_nifty500list.csv"):
        self.csv_path = csv_path
        self.companies = []
        self.companies_dict = {}  # symbol -> Company mapping
        self.load_companies()
    
    def load_companies(self):
        """Load companies from CSV and other sources"""
        try:
            # Load from CSV first
            if os.path.exists(self.csv_path):
                self._load_from_csv()
            else:
                logging.warning(f"CSV file not found: {self.csv_path}")
                self._load_sample_data()
            
            # Create lookup dictionary
            self.companies_dict = {company.symbol: company for company in self.companies}
            
            logging.info(f"Loaded {len(self.companies)} companies")
            
        except Exception as e:
            logging.error(f"Error loading companies: {e}")
            self._load_sample_data()
    
    def _load_from_csv(self):
        """Load companies from CSV file"""
        df = pd.read_csv(self.csv_path, header=None, names=['name'])
        
        for _, row in df.iterrows():
            company_name = row['name'].strip()
            symbol = self._extract_symbol(company_name)
            
            company = Company(
                symbol=symbol,
                name=company_name,
                full_name=company_name,
                exchange='NSE',
                last_updated=datetime.now()
            )
            
            self.companies.append(company)
    
    def _load_sample_data(self):
        """Load sample company data as fallback"""
        sample_companies = [
            Company(symbol="RELIANCE", name="Reliance Industries Ltd.", full_name="Reliance Industries Ltd.", exchange="NSE"),
            Company(symbol="TCS", name="Tata Consultancy Services Ltd.", full_name="Tata Consultancy Services Ltd.", exchange="NSE"),
            Company(symbol="INFY", name="Infosys Ltd.", full_name="Infosys Ltd.", exchange="NSE"),
            Company(symbol="HDFCBANK", name="HDFC Bank Ltd.", full_name="HDFC Bank Ltd.", exchange="NSE"),
        ]
        self.companies = sample_companies
    
    def _extract_symbol(self, company_name: str) -> str:
        """Extract stock symbol from company name"""
        words = company_name.split()
        
        # Handle common cases
        if company_name.upper().startswith('HDFC'):
            return 'HDFCBANK'
        elif company_name.upper().startswith('TCS'):
            return 'TCS'
        elif company_name.upper().startswith('INFY'):
            return 'INFY'
        elif company_name.upper().startswith('RELIANCE'):
            return 'RELIANCE'
        
        # Default: take first word
        return words[0].upper()
    
    def search_companies(self, query: str, limit: int = 10) -> CompanySearchResult:
        """Search companies by name or symbol"""
        import time
        start_time = time.time()
        
        query = query.lower().strip()
        results = []
        
        # Search in loaded companies
        for company in self.companies:
            name_match = query in company.name.lower()
            symbol_match = query in company.symbol.lower()
            
            if name_match or symbol_match:
                results.append(company)
                
                if len(results) >= limit:
                    break
        
        # If not enough results, try external sources
        if len(results) < limit:
            try:
                # Try Yahoo Finance
                yahoo_results = yahoo_finance_client.search_companies(query)
                for company in yahoo_results:
                    if company not in results:
                        results.append(company)
                        if len(results) >= limit:
                            break
            except Exception as e:
                logging.warning(f"Yahoo Finance search failed: {e}")
        
        search_time = time.time() - start_time
        
        return CompanySearchResult(
            companies=results,
            total_count=len(results),
            query=query,
            search_time=search_time
        )
    
    def get_company_by_symbol(self, symbol: str) -> Optional[Company]:
        """Get company details by symbol"""
        symbol = symbol.upper()
        
        # Check local cache first
        if symbol in self.companies_dict:
            return self.companies_dict[symbol]
        
        # Try external sources
        try:
            # Try Yahoo Finance
            company = yahoo_finance_client.get_company_details(symbol)
            if company:
                return company
        except Exception as e:
            logging.warning(f"Yahoo Finance lookup failed for {symbol}: {e}")
        
        return None
    
    def get_company_metadata(self, symbol: str) -> Optional[CompanyMetadata]:
        """Get additional company metadata"""
        try:
            return yahoo_finance_client.get_company_metadata(symbol)
        except Exception as e:
            logging.warning(f"Failed to get metadata for {symbol}: {e}")
            return None
    
    def refresh_company_data(self, symbol: str) -> Optional[Company]:
        """Refresh company data from external sources"""
        try:
            # Try Yahoo Finance first
            company = yahoo_finance_client.get_company_details(symbol)
            if company:
                # Update local cache
                self.companies_dict[symbol] = company
                return company
            
            # Try NSE scraper
            company = nse_scraper.get_company_details(symbol)
            if company:
                self.companies_dict[symbol] = company
                return company
                
        except Exception as e:
            logging.error(f"Error refreshing data for {symbol}: {e}")
        
        return None
    
    def get_all_companies(self) -> List[Company]:
        """Get all loaded companies"""
        return self.companies.copy()
    
    def get_companies_by_sector(self, sector: str) -> List[Company]:
        """Get companies by sector"""
        return [company for company in self.companies if company.sector and sector.lower() in company.sector.lower()]

# Global instance
company_manager = CompanyDataManager() 