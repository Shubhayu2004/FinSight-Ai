from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..company_data.manager import company_manager
from ..company_data.models import Company, CompanySearchResult

router = APIRouter(prefix="/api/company", tags=["Company Data"])

@router.get("/search")
async def search_companies(
    q: str = Query(..., description="Search query for company name or symbol"),
    limit: int = Query(10, description="Maximum number of results")
) -> CompanySearchResult:
    """Search companies by name or symbol"""
    try:
        result = company_manager.search_companies(q, limit=limit)
        return result
    except Exception as e:
        logging.error(f"Error searching companies: {e}")
        raise HTTPException(status_code=500, detail="Error searching companies")

@router.get("/{symbol}")
async def get_company_details(symbol: str) -> Company:
    """Get detailed information for a specific company"""
    try:
        company = company_manager.get_company_by_symbol(symbol)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting company details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving company details")

@router.get("/{symbol}/metadata")
async def get_company_metadata(symbol: str):
    """Get additional company metadata"""
    try:
        metadata = company_manager.get_company_metadata(symbol)
        if not metadata:
            raise HTTPException(status_code=404, detail="Company metadata not found")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting company metadata for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving company metadata")

@router.get("/list/all")
async def get_all_companies() -> List[Company]:
    """Get all available companies"""
    try:
        companies = company_manager.get_all_companies()
        return companies
    except Exception as e:
        logging.error(f"Error getting all companies: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving companies")

@router.get("/list/sector/{sector}")
async def get_companies_by_sector(sector: str) -> List[Company]:
    """Get companies by sector"""
    try:
        companies = company_manager.get_companies_by_sector(sector)
        return companies
    except Exception as e:
        logging.error(f"Error getting companies by sector {sector}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving companies by sector")

@router.post("/{symbol}/refresh")
async def refresh_company_data(symbol: str) -> Company:
    """Refresh company data from external sources"""
    try:
        company = company_manager.refresh_company_data(symbol)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found or could not be refreshed")
        return company
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error refreshing company data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error refreshing company data") 