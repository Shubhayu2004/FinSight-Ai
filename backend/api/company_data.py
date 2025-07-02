from fastapi import APIRouter, HTTPException
from backend.core.company_data import bse_company_manager

router = APIRouter(prefix="/api/companies", tags=["Company Data"])

@router.get("/dropdown")
async def get_company_dropdown():
    """Get a dropdown list of all companies (symbol and name)"""
    return bse_company_manager.get_dropdown_list()

@router.get("/{symbol}")
async def get_company_details(symbol: str):
    """Get all details for a company by symbol"""
    company = bse_company_manager.get_company_by_symbol(symbol)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company 