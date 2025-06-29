from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class DataPeriod(Enum):
    """Data periods for technical analysis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class PriceData:
    """Stock price data point"""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None

@dataclass
class TechnicalIndicators:
    """Technical indicators for a stock"""
    symbol: str
    date: datetime
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    bollinger_middle: Optional[float] = None

@dataclass
class FinancialRatios:
    """Financial ratios for a company"""
    symbol: str
    period: str  # e.g., "2023", "Q4 2023"
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None  # Return on Invested Capital
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    operating_margin: Optional[float] = None

@dataclass
class FundamentalData:
    """Fundamental financial data"""
    symbol: str
    period: str
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    total_debt: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    eps: Optional[float] = None  # Earnings per Share
    book_value_per_share: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[float] = None

@dataclass
class CompanyOverview:
    """Company overview and summary data"""
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    current_price: Optional[float] = None
    day_change: Optional[float] = None
    day_change_percent: Optional[float] = None
    year_high: Optional[float] = None
    year_low: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    beta: Optional[float] = None
    last_updated: Optional[datetime] = None

@dataclass
class TechnicalAnalysisResult:
    """Result of technical analysis"""
    symbol: str
    analysis_date: datetime
    current_price: float
    technical_indicators: TechnicalIndicators
    price_data: List[PriceData]
    recommendation: Optional[str] = None  # "Buy", "Sell", "Hold"
    confidence: Optional[float] = None
    support_levels: Optional[List[float]] = None
    resistance_levels: Optional[List[float]] = None

@dataclass
class FundamentalAnalysisResult:
    """Result of fundamental analysis"""
    symbol: str
    analysis_date: datetime
    fundamental_data: FundamentalData
    financial_ratios: FinancialRatios
    company_overview: CompanyOverview
    valuation_metrics: Dict[str, float]
    peer_comparison: Optional[Dict[str, float]] = None
    recommendation: Optional[str] = None
    confidence: Optional[float] = None 