from typing import List, Optional, Dict
import logging
from datetime import datetime, timedelta
import numpy as np

from .models import (
    PriceData, TechnicalIndicators, FundamentalData, FinancialRatios,
    CompanyOverview, TechnicalAnalysisResult, FundamentalAnalysisResult
)
from .api_clients.alpha_vantage import alpha_vantage_client

class TechnicalDataManager:
    """Manager for technical and fundamental data"""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get_company_overview(self, symbol: str) -> Optional[CompanyOverview]:
        """Get company overview data"""
        cache_key = f"overview_{symbol}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        # Fetch from API
        overview = alpha_vantage_client.get_company_overview(symbol)
        
        if overview:
            self.cache[cache_key] = (overview, datetime.now())
        
        return overview
    
    def get_price_data(self, symbol: str, days: int = 30) -> List[PriceData]:
        """Get historical price data"""
        cache_key = f"price_{symbol}_{days}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        # Fetch from API
        price_data = alpha_vantage_client.get_daily_price_data(symbol)
        
        # Limit to requested days
        if price_data and days > 0:
            price_data = price_data[-days:]
        
        if price_data:
            self.cache[cache_key] = (price_data, datetime.now())
        
        return price_data
    
    def get_technical_indicators(self, symbol: str) -> Optional[TechnicalIndicators]:
        """Get technical indicators"""
        cache_key = f"technical_{symbol}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        # Fetch from API
        indicators = alpha_vantage_client.get_technical_indicators(symbol)
        
        if indicators:
            self.cache[cache_key] = (indicators, datetime.now())
        
        return indicators
    
    def perform_technical_analysis(self, symbol: str) -> Optional[TechnicalAnalysisResult]:
        """Perform comprehensive technical analysis"""
        try:
            # Get price data
            price_data = self.get_price_data(symbol, days=200)
            if not price_data:
                return None
            
            # Get technical indicators
            indicators = self.get_technical_indicators(symbol)
            if not indicators:
                return None
            
            current_price = price_data[-1].close if price_data else 0
            
            # Calculate support and resistance levels
            support_levels = self._calculate_support_levels(price_data)
            resistance_levels = self._calculate_resistance_levels(price_data)
            
            # Generate recommendation
            recommendation, confidence = self._generate_technical_recommendation(
                indicators, current_price, support_levels, resistance_levels
            )
            
            result = TechnicalAnalysisResult(
                symbol=symbol,
                analysis_date=datetime.now(),
                current_price=current_price,
                technical_indicators=indicators,
                price_data=price_data,
                recommendation=recommendation,
                confidence=confidence,
                support_levels=support_levels,
                resistance_levels=resistance_levels
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error performing technical analysis for {symbol}: {e}")
            return None
    
    def _calculate_support_levels(self, price_data: List[PriceData]) -> List[float]:
        """Calculate support levels using recent lows"""
        if not price_data:
            return []
        
        # Get recent lows (last 50 days)
        recent_data = price_data[-50:] if len(price_data) > 50 else price_data
        lows = [point.low for point in recent_data]
        
        # Find significant support levels
        support_levels = []
        min_low = min(lows)
        max_low = max(lows)
        
        # Create support levels at 5% intervals
        for i in range(5):
            level = min_low + (max_low - min_low) * i / 4
            support_levels.append(round(level, 2))
        
        return sorted(support_levels)
    
    def _calculate_resistance_levels(self, price_data: List[PriceData]) -> List[float]:
        """Calculate resistance levels using recent highs"""
        if not price_data:
            return []
        
        # Get recent highs (last 50 days)
        recent_data = price_data[-50:] if len(price_data) > 50 else price_data
        highs = [point.high for point in recent_data]
        
        # Find significant resistance levels
        resistance_levels = []
        min_high = min(highs)
        max_high = max(highs)
        
        # Create resistance levels at 5% intervals
        for i in range(5):
            level = min_high + (max_high - min_high) * i / 4
            resistance_levels.append(round(level, 2))
        
        return sorted(resistance_levels)
    
    def _generate_technical_recommendation(
        self, 
        indicators: TechnicalIndicators, 
        current_price: float,
        support_levels: List[float],
        resistance_levels: List[float]
    ) -> tuple[str, float]:
        """Generate buy/sell/hold recommendation based on technical indicators"""
        signals = []
        confidence_factors = []
        
        # RSI analysis
        if indicators.rsi:
            if indicators.rsi < 30:
                signals.append("BUY")
                confidence_factors.append(0.8)
            elif indicators.rsi > 70:
                signals.append("SELL")
                confidence_factors.append(0.8)
            else:
                signals.append("HOLD")
                confidence_factors.append(0.6)
        
        # Moving average analysis
        if indicators.sma_20 and indicators.sma_50:
            if current_price > indicators.sma_20 > indicators.sma_50:
                signals.append("BUY")
                confidence_factors.append(0.7)
            elif current_price < indicators.sma_20 < indicators.sma_50:
                signals.append("SELL")
                confidence_factors.append(0.7)
            else:
                signals.append("HOLD")
                confidence_factors.append(0.5)
        
        # MACD analysis
        if indicators.macd and indicators.macd_signal:
            if indicators.macd > indicators.macd_signal:
                signals.append("BUY")
                confidence_factors.append(0.6)
            else:
                signals.append("SELL")
                confidence_factors.append(0.6)
        
        # Bollinger Bands analysis
        if indicators.bollinger_upper and indicators.bollinger_lower:
            if current_price < indicators.bollinger_lower:
                signals.append("BUY")
                confidence_factors.append(0.7)
            elif current_price > indicators.bollinger_upper:
                signals.append("SELL")
                confidence_factors.append(0.7)
            else:
                signals.append("HOLD")
                confidence_factors.append(0.5)
        
        # Determine final recommendation
        if not signals:
            return "HOLD", 0.5
        
        # Count signals
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        hold_count = signals.count("HOLD")
        
        if buy_count > sell_count and buy_count > hold_count:
            recommendation = "BUY"
        elif sell_count > buy_count and sell_count > hold_count:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        # Calculate confidence
        confidence = np.mean(confidence_factors) if confidence_factors else 0.5
        
        return recommendation, confidence
    
    def get_financial_ratios(self, symbol: str) -> Optional[FinancialRatios]:
        """Get financial ratios (placeholder - would integrate with financial APIs)"""
        # This would typically integrate with financial data providers
        # For now, return sample data
        return FinancialRatios(
            symbol=symbol,
            period="2023",
            pe_ratio=15.5,
            pb_ratio=2.1,
            debt_to_equity=0.3,
            current_ratio=1.8,
            quick_ratio=1.2,
            roe=12.5,
            roa=8.2,
            roic=10.1,
            gross_margin=45.2,
            net_margin=12.8,
            operating_margin=18.5
        )
    
    def perform_fundamental_analysis(self, symbol: str) -> Optional[FundamentalAnalysisResult]:
        """Perform fundamental analysis"""
        try:
            # Get company overview
            overview = self.get_company_overview(symbol)
            if not overview:
                return None
            
            # Get financial ratios
            ratios = self.get_financial_ratios(symbol)
            if not ratios:
                return None
            
            # Create fundamental data (placeholder)
            fundamental_data = FundamentalData(
                symbol=symbol,
                period="2023",
                revenue=1000000000,  # 1B
                net_income=125000000,  # 125M
                total_assets=2000000000,  # 2B
                total_equity=1500000000,  # 1.5B
                eps=2.5,
                market_cap=overview.market_cap
            )
            
            # Calculate valuation metrics
            valuation_metrics = self._calculate_valuation_metrics(
                fundamental_data, ratios, overview
            )
            
            # Generate recommendation
            recommendation, confidence = self._generate_fundamental_recommendation(
                ratios, valuation_metrics
            )
            
            result = FundamentalAnalysisResult(
                symbol=symbol,
                analysis_date=datetime.now(),
                fundamental_data=fundamental_data,
                financial_ratios=ratios,
                company_overview=overview,
                valuation_metrics=valuation_metrics,
                recommendation=recommendation,
                confidence=confidence
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error performing fundamental analysis for {symbol}: {e}")
            return None
    
    def _calculate_valuation_metrics(
        self, 
        fundamental_data: FundamentalData, 
        ratios: FinancialRatios,
        overview: CompanyOverview
    ) -> Dict[str, float]:
        """Calculate valuation metrics"""
        metrics = {}
        
        if fundamental_data.revenue and fundamental_data.net_income:
            metrics['price_to_sales'] = (overview.current_price or 0) / (fundamental_data.revenue / 1000000)  # P/S ratio
            metrics['price_to_earnings'] = ratios.pe_ratio or 0
            metrics['price_to_book'] = ratios.pb_ratio or 0
        
        if fundamental_data.total_equity:
            metrics['book_value_per_share'] = fundamental_data.total_equity / 1000000  # Simplified
        
        return metrics
    
    def _generate_fundamental_recommendation(
        self, 
        ratios: FinancialRatios, 
        valuation_metrics: Dict[str, float]
    ) -> tuple[str, float]:
        """Generate fundamental recommendation"""
        signals = []
        confidence_factors = []
        
        # P/E ratio analysis
        if ratios.pe_ratio:
            if ratios.pe_ratio < 15:
                signals.append("BUY")
                confidence_factors.append(0.7)
            elif ratios.pe_ratio > 25:
                signals.append("SELL")
                confidence_factors.append(0.7)
            else:
                signals.append("HOLD")
                confidence_factors.append(0.6)
        
        # ROE analysis
        if ratios.roe:
            if ratios.roe > 15:
                signals.append("BUY")
                confidence_factors.append(0.8)
            elif ratios.roe < 8:
                signals.append("SELL")
                confidence_factors.append(0.8)
            else:
                signals.append("HOLD")
                confidence_factors.append(0.6)
        
        # Debt analysis
        if ratios.debt_to_equity:
            if ratios.debt_to_equity < 0.5:
                signals.append("BUY")
                confidence_factors.append(0.6)
            elif ratios.debt_to_equity > 1.0:
                signals.append("SELL")
                confidence_factors.append(0.6)
            else:
                signals.append("HOLD")
                confidence_factors.append(0.5)
        
        # Determine final recommendation
        if not signals:
            return "HOLD", 0.5
        
        buy_count = signals.count("BUY")
        sell_count = signals.count("SELL")
        hold_count = signals.count("HOLD")
        
        if buy_count > sell_count and buy_count > hold_count:
            recommendation = "BUY"
        elif sell_count > buy_count and sell_count > hold_count:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"
        
        confidence = np.mean(confidence_factors) if confidence_factors else 0.5
        
        return recommendation, confidence

# Global instance
technical_manager = TechnicalDataManager() 