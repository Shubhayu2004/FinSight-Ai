from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import os
import math
import requests
import importlib.util
from urllib.parse import quote

# Create the FastAPI app
app = FastAPI(title="AI Finance Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Path to the CSV file (relative to this file)
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

@app.get("/api/companies/{company_name}/annual_report")
def get_annual_report(company_name: str):
    df = load_companies()
    # Find the row by issuer name (case-insensitive)
    company_row = df[df['Issuer Name'].str.lower() == company_name.lower()]
    if company_row.empty:
        raise HTTPException(status_code=404, detail="Company not found in database")
    symbol = company_row.iloc[0]['Security Id']
    issuer = company_row.iloc[0]['Issuer Name']
    # NSE API call
    nse_url = (
        f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={symbol}&issuer={quote(issuer)}"
    )
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-annual-reports"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    resp = session.get(nse_url, headers=headers)
    try:
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse NSE response")
    if not data.get("data"):
        raise HTTPException(status_code=404, detail="No annual report found on NSE")
    latest_report = data["data"][0]["fileName"]
    # Download the PDF/ZIP
    ext = os.path.splitext(latest_report)[1]
    safe_name = company_name.replace(" ", "_").replace("/", "_")
    pdf_path = os.path.join(REPORTS_DIR, f"{safe_name}_annual_report{ext}")
    try:
        file_resp = session.get(latest_report, stream=True, timeout=30)
        with open(pdf_path, "wb") as f:
            for chunk in file_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {e}")
    return {"view_url": f"/api/companies/{company_name}/annual_report/view"}

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