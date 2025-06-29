import pandas as pd
import os
from typing import List, Dict, Optional

class CompanyDataManager:
    def __init__(self, csv_path: str = "../financial_data/ind_nifty500list.csv"):
        self.companies = []
        self.load_companies(csv_path)
    
    def load_companies(self, csv_path: str):
        """Load company data from CSV file"""
        try:
            # Read CSV - assuming it has company names in a single column
            df = pd.read_csv(csv_path, header=None, names=['name'])
            
            # Create company objects with symbol extraction
            for _, row in df.iterrows():
                company_name = row['name'].strip()
                # Extract symbol from name (usually the first word or acronym)
                symbol = self._extract_symbol(company_name)
                
                self.companies.append({
                    'name': company_name,
                    'symbol': symbol,
                    'full_name': company_name
                })
            
            print(f"Loaded {len(self.companies)} companies from {csv_path}")
            
        except Exception as e:
            print(f"Error loading companies: {e}")
            # Fallback to sample data
            self.companies = [
                {"symbol": "RELIANCE", "name": "Reliance Industries Ltd.", "full_name": "Reliance Industries Ltd."},
                {"symbol": "TCS", "name": "Tata Consultancy Services Ltd.", "full_name": "Tata Consultancy Services Ltd."},
                {"symbol": "INFY", "name": "Infosys Ltd.", "full_name": "Infosys Ltd."},
                {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd.", "full_name": "HDFC Bank Ltd."},
            ]
    
    def _extract_symbol(self, company_name: str) -> str:
        """Extract stock symbol from company name"""
        # Simple extraction - take first word or common acronyms
        words = company_name.split()
        
        # Handle common cases
        if len(words) == 1:
            return words[0].upper()
        
        # Check for common acronyms
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
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict]:
        """Search companies by name or symbol"""
        query = query.lower().strip()
        results = []
        
        for company in self.companies:
            name_match = query in company['name'].lower()
            symbol_match = query in company['symbol'].lower()
            
            if name_match or symbol_match:
                results.append(company)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_company_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get company details by symbol"""
        symbol = symbol.upper()
        for company in self.companies:
            if company['symbol'] == symbol:
                return company
        return None

# Global instance
company_manager = CompanyDataManager() 