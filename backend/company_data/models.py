from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Company:
    """Company data model"""
    symbol: str
    name: str
    full_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    listing_date: Optional[datetime] = None
    exchange: Optional[str] = None  # NSE, BSE, etc.
    isin: Optional[str] = None
    last_updated: Optional[datetime] = None

@dataclass
class CompanySearchResult:
    """Search result for company queries"""
    companies: List[Company]
    total_count: int
    query: str
    search_time: float

@dataclass
class CompanyMetadata:
    """Additional company metadata"""
    company_id: str
    website: Optional[str] = None
    investor_relations_url: Optional[str] = None
    annual_report_url: Optional[str] = None
    description: Optional[str] = None
    employees: Optional[int] = None
    headquarters: Optional[str] = None 