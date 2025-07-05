from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import os
import math
import requests
import importlib.util
from urllib.parse import quote
import traceback
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="AI Finance Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_PATH = os.path.join(os.path.dirname(__file__), '../company data/archive/BSE_Equity.csv')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '../company data/archive/reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_companies():
    try:
        df = pd.read_csv(CSV_PATH)
        return df
    except Exception as e:
        print(f"Error loading companies: {e}")
        return pd.DataFrame([])

@app.get("/api/companies/dropdown")
def get_company_dropdown():
    df = load_companies()
    if df.empty:
        return []
    return [
        {
            'symbol': row['Security Id'],
            'name': row['Issuer Name']
        }
        for _, row in df.iterrows()
    ]

@app.get("/api/companies/{symbol}")
def get_company_details(symbol: str):
    df = load_companies()
    if df.empty:
        raise HTTPException(status_code=500, detail="Company data not available")
    symbol = symbol.upper()
    company = df[df['Security Id'].str.upper() == symbol]
    if company.empty:
        raise HTTPException(status_code=404, detail="Company not found")
    row = company.iloc[0].to_dict()
    # Sanitize float values for JSON
    for k, v in row.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            row[k] = None
    return row

@app.get("/api/companies/{symbol}/annual_report")
def get_annual_report(symbol: str):
    try:
        # Dynamically import the scraper
        scraper_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../company data/annual report scraper.py')
        )
        spec = importlib.util.spec_from_file_location("annual_report_scraper", scraper_path)
        if spec is None or spec.loader is None:
            print("Failed to import annual_report_scraper module.")
            raise HTTPException(status_code=500, detail="Failed to import scraper module.")
        scraper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scraper)
        
        print(f"Fetching annual report for symbol: {symbol}")
        
        # Create download path
        safe_name = symbol.replace(" ", "_").replace("/", "_")
        download_path = os.path.join(REPORTS_DIR, f"{safe_name}_annual_report.pdf")
        
        # Call the scraper function
        result = scraper.scrape_nse_latest_annual_report(symbol, download_path, headless=True)
        
        if not result.get('success'):
            print(f"No annual report found for symbol: {symbol}")
            raise HTTPException(status_code=404, detail=result.get('error', 'No annual report found on NSE'))
        
        print(f"Latest report file link: {result.get('pdf_url')}")
        print(f"Report title: {result.get('title')}")
        
        if 'local_path' in result:
            print(f"PDF downloaded to: {result['local_path']}")
            return {"view_url": f"/api/companies/{symbol}/annual_report/view"}
        else:
            # If download failed, return the direct PDF URL
            return {"pdf_url": result.get('pdf_url'), "title": result.get('title')}
            
    except Exception as e:
        print(f"Error in get_annual_report: {e}")
        traceback.print_exc()
        raise

@app.get("/api/companies/{company_name}/annual_report/view")
def view_annual_report(company_name: str):
    # Try both .pdf and .zip extensions
    safe_name = company_name.replace(" ", "_").replace("/", "_")
    pdf_path = os.path.join(REPORTS_DIR, f"{safe_name}_annual_report.pdf")
    zip_path = os.path.join(REPORTS_DIR, f"{safe_name}_annual_report.zip")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"{company_name}_annual_report.pdf")
    elif os.path.exists(zip_path):
        return FileResponse(zip_path, media_type="application/zip", filename=f"{company_name}_annual_report.zip")
    else:
        raise HTTPException(status_code=404, detail="Report not found. Please fetch the report first.")

@app.get("/")
def root():
    return {"message": "AI Finance Agent API is running."} 