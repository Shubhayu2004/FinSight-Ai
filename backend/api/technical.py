from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..technical_data.manager import technical_manager
from ..technical_data.models import (
    TechnicalAnalysisResult, FundamentalAnalysisResult,
    CompanyOverview, TechnicalIndicators, FinancialRatios
)

router = APIRouter(prefix="/api/technical", tags=["Technical Data"])

@router.get("/{symbol}/overview")
async def get_company_overview(symbol: str) -> CompanyOverview:
    """Get company overview and basic information"""
    try:
        overview = technical_manager.get_company_overview(symbol)
        if not overview:
            raise HTTPException(status_code=404, detail="Company overview not found")
        return overview
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting company overview for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving company overview")

@router.get("/{symbol}/price")
async def get_price_data(
    symbol: str,
    days: int = Query(30, description="Number of days of price data")
):
    """Get historical price data"""
    try:
        price_data = technical_manager.get_price_data(symbol, days=days)
        return {
            "symbol": symbol,
            "days": days,
            "data_points": len(price_data),
            "price_data": price_data
        }
    except Exception as e:
        logging.error(f"Error getting price data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving price data")

@router.get("/{symbol}/indicators")
async def get_technical_indicators(symbol: str) -> TechnicalIndicators:
    """Get technical indicators"""
    try:
        indicators = technical_manager.get_technical_indicators(symbol)
        if not indicators:
            raise HTTPException(status_code=404, detail="Technical indicators not found")
        return indicators
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting technical indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving technical indicators")

@router.get("/{symbol}/fundamentals")
async def get_financial_ratios(symbol: str) -> FinancialRatios:
    """Get financial ratios and fundamental data"""
    try:
        ratios = technical_manager.get_financial_ratios(symbol)
        if not ratios:
            raise HTTPException(status_code=404, detail="Financial ratios not found")
        return ratios
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting financial ratios for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving financial ratios")

@router.get("/{symbol}/analysis/technical")
async def perform_technical_analysis(symbol: str) -> TechnicalAnalysisResult:
    """Perform comprehensive technical analysis"""
    try:
        analysis = technical_manager.perform_technical_analysis(symbol)
        if not analysis:
            raise HTTPException(status_code=404, detail="Technical analysis could not be performed")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error performing technical analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error performing technical analysis")

@router.get("/{symbol}/analysis/fundamental")
async def perform_fundamental_analysis(symbol: str) -> FundamentalAnalysisResult:
    """Perform fundamental analysis"""
    try:
        analysis = technical_manager.perform_fundamental_analysis(symbol)
        if not analysis:
            raise HTTPException(status_code=404, detail="Fundamental analysis could not be performed")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error performing fundamental analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error performing fundamental analysis")

@router.get("/{symbol}/analysis/complete")
async def perform_complete_analysis(symbol: str):
    """Perform both technical and fundamental analysis"""
    try:
        technical = technical_manager.perform_technical_analysis(symbol)
        fundamental = technical_manager.perform_fundamental_analysis(symbol)
        overview = technical_manager.get_company_overview(symbol)
        
        return {
            "symbol": symbol,
            "analysis_date": technical.analysis_date if technical else None,
            "technical_analysis": technical,
            "fundamental_analysis": fundamental,
            "company_overview": overview,
            "summary": {
                "technical_recommendation": technical.recommendation if technical else None,
                "fundamental_recommendation": fundamental.recommendation if fundamental else None,
                "technical_confidence": technical.confidence if technical else None,
                "fundamental_confidence": fundamental.confidence if fundamental else None
            }
        }
    except Exception as e:
        logging.error(f"Error performing complete analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error performing complete analysis")

@router.get("/{symbol}/recommendation")
async def get_investment_recommendation(symbol: str):
    """Get investment recommendation based on technical and fundamental analysis"""
    try:
        technical = technical_manager.perform_technical_analysis(symbol)
        fundamental = technical_manager.perform_fundamental_analysis(symbol)
        
        if not technical or not fundamental:
            raise HTTPException(status_code=404, detail="Could not generate recommendation")
        
        # Combine recommendations (simplified logic)
        technical_weight = 0.4
        fundamental_weight = 0.6
        
        # Convert recommendations to scores
        def recommendation_to_score(rec):
            if rec == "BUY":
                return 1.0
            elif rec == "SELL":
                return -1.0
            else:
                return 0.0
        
        technical_score = recommendation_to_score(technical.recommendation)
        fundamental_score = recommendation_to_score(fundamental.recommendation)
        
        # Calculate weighted score
        weighted_score = (technical_score * technical_weight + 
                         fundamental_score * fundamental_weight)
        
        # Determine final recommendation
        if weighted_score > 0.3:
            final_recommendation = "BUY"
        elif weighted_score < -0.3:
            final_recommendation = "SELL"
        else:
            final_recommendation = "HOLD"
        
        # Calculate confidence
        confidence = (technical.confidence * technical_weight + 
                     fundamental.confidence * fundamental_weight)
        
        return {
            "symbol": symbol,
            "recommendation": final_recommendation,
            "confidence": confidence,
            "technical_analysis": {
                "recommendation": technical.recommendation,
                "confidence": technical.confidence
            },
            "fundamental_analysis": {
                "recommendation": fundamental.recommendation,
                "confidence": fundamental.confidence
            },
            "reasoning": {
                "technical_factors": [
                    f"RSI: {technical.technical_indicators.rsi:.2f}" if technical.technical_indicators.rsi else "RSI: N/A",
                    f"SMA 20/50: {'Bullish' if technical.technical_indicators.sma_20 and technical.technical_indicators.sma_50 and technical.technical_indicators.sma_20 > technical.technical_indicators.sma_50 else 'Bearish' if technical.technical_indicators.sma_20 and technical.technical_indicators.sma_50 and technical.technical_indicators.sma_20 < technical.technical_indicators.sma_50 else 'Neutral'}"
                ],
                "fundamental_factors": [
                    f"P/E Ratio: {fundamental.financial_ratios.pe_ratio:.2f}" if fundamental.financial_ratios.pe_ratio else "P/E Ratio: N/A",
                    f"ROE: {fundamental.financial_ratios.roe:.2f}%" if fundamental.financial_ratios.roe else "ROE: N/A",
                    f"Debt/Equity: {fundamental.financial_ratios.debt_to_equity:.2f}" if fundamental.financial_ratios.debt_to_equity else "Debt/Equity: N/A"
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting investment recommendation for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error generating investment recommendation") 