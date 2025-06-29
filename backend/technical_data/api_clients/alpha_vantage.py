import requests
from typing import List, Optional, Dict
import logging
from datetime import datetime, timedelta
import time

from ..models import PriceData, TechnicalIndicators, FundamentalData, FinancialRatios, CompanyOverview

class AlphaVantageClient:
    """Client for Alpha Vantage API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo"  # Use demo key if none provided
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        
        # Rate limiting: 5 requests per minute for free tier
        self.last_request_time = 0
        self.min_request_interval = 12  # seconds
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_daily_price_data(self, symbol: str, outputsize: str = "compact") -> List[PriceData]:
        """Get daily price data for a symbol"""
        self._rate_limit()
        
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "Error Message" in data:
                logging.error(f"Alpha Vantage error: {data['Error Message']}")
                return []
            
            time_series = data.get('Time Series (Daily)', {})
            price_data = []
            
            for date_str, values in time_series.items():
                date = datetime.strptime(date_str, '%Y-%m-%d')
                
                price_point = PriceData(
                    date=date,
                    open=float(values.get('1. open', 0)),
                    high=float(values.get('2. high', 0)),
                    low=float(values.get('3. low', 0)),
                    close=float(values.get('4. close', 0)),
                    volume=int(values.get('5. volume', 0)),
                    adjusted_close=float(values.get('5. adjusted close', 0))
                )
                price_data.append(price_point)
            
            # Sort by date (oldest first)
            price_data.sort(key=lambda x: x.date)
            
            return price_data
            
        except Exception as e:
            logging.error(f"Error fetching daily price data for {symbol}: {e}")
            return []
    
    def get_technical_indicators(self, symbol: str) -> Optional[TechnicalIndicators]:
        """Get technical indicators for a symbol"""
        self._rate_limit()
        
        try:
            # Get SMA indicators
            sma_20 = self._get_sma(symbol, 20)
            sma_50 = self._get_sma(symbol, 50)
            sma_200 = self._get_sma(symbol, 200)
            
            # Get RSI
            rsi = self._get_rsi(symbol)
            
            # Get MACD
            macd_data = self._get_macd(symbol)
            
            # Get Bollinger Bands
            bb_data = self._get_bollinger_bands(symbol)
            
            indicators = TechnicalIndicators(
                symbol=symbol,
                date=datetime.now(),
                sma_20=sma_20,
                sma_50=sma_50,
                sma_200=sma_200,
                rsi=rsi,
                macd=macd_data.get('macd') if macd_data else None,
                macd_signal=macd_data.get('signal') if macd_data else None,
                bollinger_upper=bb_data.get('upper') if bb_data else None,
                bollinger_lower=bb_data.get('lower') if bb_data else None,
                bollinger_middle=bb_data.get('middle') if bb_data else None
            )
            
            return indicators
            
        except Exception as e:
            logging.error(f"Error fetching technical indicators for {symbol}: {e}")
            return None
    
    def _get_sma(self, symbol: str, period: int) -> Optional[float]:
        """Get Simple Moving Average"""
        try:
            params = {
                'function': 'SMA',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': period,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            technical_analysis = data.get('Technical Analysis: SMA', {})
            
            if technical_analysis:
                # Get the most recent value
                latest_date = max(technical_analysis.keys())
                return float(technical_analysis[latest_date]['SMA'])
            
            return None
            
        except Exception as e:
            logging.warning(f"Error fetching SMA {period} for {symbol}: {e}")
            return None
    
    def _get_rsi(self, symbol: str) -> Optional[float]:
        """Get Relative Strength Index"""
        try:
            params = {
                'function': 'RSI',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            technical_analysis = data.get('Technical Analysis: RSI', {})
            
            if technical_analysis:
                latest_date = max(technical_analysis.keys())
                return float(technical_analysis[latest_date]['RSI'])
            
            return None
            
        except Exception as e:
            logging.warning(f"Error fetching RSI for {symbol}: {e}")
            return None
    
    def _get_macd(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get MACD (Moving Average Convergence Divergence)"""
        try:
            params = {
                'function': 'MACD',
                'symbol': symbol,
                'interval': 'daily',
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            technical_analysis = data.get('Technical Analysis: MACD', {})
            
            if technical_analysis:
                latest_date = max(technical_analysis.keys())
                latest_data = technical_analysis[latest_date]
                
                return {
                    'macd': float(latest_data['MACD']),
                    'signal': float(latest_data['MACD_Signal'])
                }
            
            return None
            
        except Exception as e:
            logging.warning(f"Error fetching MACD for {symbol}: {e}")
            return None
    
    def _get_bollinger_bands(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get Bollinger Bands"""
        try:
            params = {
                'function': 'BBANDS',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 20,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            technical_analysis = data.get('Technical Analysis: BBANDS', {})
            
            if technical_analysis:
                latest_date = max(technical_analysis.keys())
                latest_data = technical_analysis[latest_date]
                
                return {
                    'upper': float(latest_data['Real Upper Band']),
                    'middle': float(latest_data['Real Middle Band']),
                    'lower': float(latest_data['Real Lower Band'])
                }
            
            return None
            
        except Exception as e:
            logging.warning(f"Error fetching Bollinger Bands for {symbol}: {e}")
            return None
    
    def get_company_overview(self, symbol: str) -> Optional[CompanyOverview]:
        """Get company overview and fundamental data"""
        self._rate_limit()
        
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "Error Message" in data:
                logging.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            overview = CompanyOverview(
                symbol=symbol,
                company_name=data.get('Name', symbol),
                sector=data.get('Sector'),
                industry=data.get('Industry'),
                market_cap=float(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else None,
                current_price=float(data.get('LatestPrice', 0)) if data.get('LatestPrice') else None,
                beta=float(data.get('Beta', 0)) if data.get('Beta') else None,
                last_updated=datetime.now()
            )
            
            return overview
            
        except Exception as e:
            logging.error(f"Error fetching company overview for {symbol}: {e}")
            return None

# Global instance
alpha_vantage_client = AlphaVantageClient() 