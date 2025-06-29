# FinSight AI Backend

This is the backend service for FinSight AI, a financial investment report analyzer for Indian stocks.

## Features
- Company search and autocomplete (NSE/BSE)
- Scrape and download latest annual reports (NSE, BSE, company sites)
- Parse PDF/HTML reports and extract text
- LLM inference API (local or remote)
- Interactive chatbot API for financial Q&A
- Modular design for future extensions (vector DB, voice, sentiment, etc.)

## Tech Stack
- Python 3.10+
- FastAPI
- PDF parsing: pdfplumber, PyMuPDF
- Web scraping: requests, BeautifulSoup, Selenium/Playwright
- LLM: Local (Unsloth/HuggingFace) or API
- DB: SQLite (default), PostgreSQL (optional)

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

## Directory Structure
- `main.py` - FastAPI entrypoint
- `api/` - API route modules
- `core/` - Core logic (scraper, parser, LLM, utils)
- `db/` - Database models and setup

## Development
- Add your NSE/BSE API keys or scraping credentials to `.env` if needed.
- For local LLM, ensure the model is downloaded and accessible to the backend.

---

See the main project README for full-stack setup and integration. 