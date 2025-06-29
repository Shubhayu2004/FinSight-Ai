from fastapi import APIRouter, Query
from typing import List

router = APIRouter()

# Placeholder: In production, load from CSV or scrape NSE/BSE
SAMPLE_COMPANIES = [
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd."},
    {"symbol": "TCS", "name": "Tata Consultancy Services Ltd."},
    {"symbol": "INFY", "name": "Infosys Ltd."},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd."},
]

@router.get("/search", response_model=List[dict])
def search_companies(q: str = Query(..., description="Search query for company name or symbol")):
    # Simple filter for demo; replace with real search logic
    results = [c for c in SAMPLE_COMPANIES if q.lower() in c["name"].lower() or q.lower() in c["symbol"].lower()]
    return results 