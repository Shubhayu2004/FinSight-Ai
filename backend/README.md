# FinSight AI Backend

This is the backend service for FinSight AI, a financial investment report analyzer for Indian stocks.

## 🏗️ Modular Architecture

The backend is organized into four main components:

```
backend/
├── company_data/           # Component 1: Company names and symbols
│   ├── scrapers/          # Web scrapers for NSE/BSE data
│   ├── api_clients/       # API clients for stock data
│   ├── models.py          # Company data models
│   └── manager.py         # Company data manager
│
├── report_extractor/       # Component 2: Annual report extraction
│   ├── scrapers/          # Web scrapers for annual reports
│   ├── parsers/           # PDF/HTML parsers
│   ├── downloaders/       # Report downloaders
│   └── manager.py         # Report extraction manager
│
├── technical_data/         # Component 3: Technical details and fundamentals
│   ├── scrapers/          # Technical data scrapers
│   ├── api_clients/       # Financial API clients
│   ├── calculators/       # Financial calculations
│   └── manager.py         # Technical data manager
│
├── chatbot/               # Component 4: LLM chatbot
│   ├── llm_client.py      # LLM integration
│   ├── context_manager.py # Context management
│   ├── prompt_engineer.py # Prompt engineering
│   └── manager.py         # Chatbot manager
│
├── api/                   # FastAPI routes
│   ├── company.py         # Company endpoints
│   ├── reports.py         # Report endpoints
│   ├── technical.py       # Technical data endpoints
│   └── chat.py            # Chatbot endpoints
│
├── core/                  # Shared utilities
│   ├── database.py        # Database setup
│   ├── config.py          # Configuration
│   └── utils.py           # Shared utilities
│
└── main.py                # FastAPI entrypoint
```

## 🎯 Component Overview

### 1. Company Data (`company_data/`)
- **Purpose**: Fetch and manage company names, symbols, and basic info
- **Sources**: NSE, BSE, Yahoo Finance, etc.
- **Features**: 
  - Web scraping for company lists
  - API integration for real-time data
  - Symbol validation and normalization
  - Company metadata management

### 2. Report Extractor (`report_extractor/`)
- **Purpose**: Extract annual reports and financial documents
- **Sources**: Company websites, NSE, BSE, SEBI
- **Features**:
  - Automated report discovery
  - PDF/HTML parsing
  - Document text extraction
  - Section identification (MD&A, Risk Factors, etc.)

### 3. Technical Data (`technical_data/`)
- **Purpose**: Fetch technical details and fundamental data
- **Sources**: Financial APIs, stock exchanges
- **Features**:
  - Price data and technical indicators
  - Financial ratios and fundamentals
  - Historical performance data
  - Peer comparison data

### 4. Chatbot (`chatbot/`)
- **Purpose**: LLM-powered Q&A system
- **Features**:
  - Fine-tuned LLM integration
  - Context-aware responses
  - Report-based Q&A
  - Session management

## 🚀 Quick Start

1. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Run Backend:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Test Components:**
   ```bash
   python test_components.py
   ```

## 📋 Development Status

### Component 1: Company Data ✅
- [x] Basic structure
- [x] CSV data integration
- [ ] NSE/BSE web scraping
- [ ] Real-time API integration

### Component 2: Report Extractor ✅
- [x] Basic structure
- [x] PDF/HTML parsing
- [ ] Automated report discovery
- [ ] Section extraction

### Component 3: Technical Data 🚧
- [x] Basic structure
- [ ] Financial API integration
- [ ] Technical indicators
- [ ] Fundamental data

### Component 4: Chatbot ✅
- [x] LLM integration
- [x] Basic Q&A
- [ ] Context management
- [ ] Session handling

## 🔧 Configuration

Create a `.env` file:
```env
# API Keys
ALPHA_VANTAGE_API_KEY=your_key
YAHOO_FINANCE_API_KEY=your_key
NSE_API_KEY=your_key

# Database
DATABASE_URL=sqlite:///./finsight.db

# LLM
LLM_MODEL_PATH=../llm fine tune/l3_finagent_step60/l3_finagent_step60/
```

## 📚 API Endpoints

### Company Data
- `GET /api/company/search` - Search companies
- `GET /api/company/{symbol}` - Get company details
- `GET /api/company/list` - List all companies

### Report Extractor
- `POST /api/reports/fetch/{symbol}` - Fetch latest report
- `POST /api/reports/upload` - Upload report
- `GET /api/reports/{symbol}/latest` - Get latest report

### Technical Data
- `GET /api/technical/{symbol}/fundamentals` - Get fundamentals
- `GET /api/technical/{symbol}/price` - Get price data
- `GET /api/technical/{symbol}/ratios` - Get financial ratios

### Chatbot
- `POST /api/chat/ask` - Ask question
- `GET /api/chat/session/{id}` - Get chat history
- `DELETE /api/chat/session/{id}` - Clear session

---

See the main project README for full-stack setup and integration. 