# FinSight AI - Financial Investment Report Analyzer

A web-based application for analyzing financial investment reports of Indian stocks using AI. FinSight AI allows users to search companies, automatically fetch annual reports, parse them, and ask questions using a fine-tuned LLM.

## 🚀 Features

- **Company Search**: Search and select any NSE/BSE-listed company with autocomplete
- **Report Fetching**: Automatically scrape latest annual reports from official sites
- **Document Parsing**: Parse PDF/HTML reports and extract usable text context
- **AI Chatbot**: Interactive Q&A using a fine-tuned LLM for financial analysis
- **Modular Architecture**: Easy to extend with vector DB, voice queries, sentiment analysis

## 🏗️ Architecture

```
FinSightAI/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Core logic modules
│   ├── db/                 # Database models
│   └── main.py             # FastAPI entrypoint
├── frontend/               # React frontend (coming soon)
├── llm fine tune/          # Fine-tuned LLM models
├── financial_data/         # NSE/BSE data
└── data/                   # Downloaded reports, cache
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **LLM**: Local fine-tuned LLaMA-3 (Unsloth)
- **Parsing**: pdfplumber, PyMuPDF, BeautifulSoup
- **Scraping**: requests, Selenium/Playwright
- **Database**: SQLite (default), PostgreSQL (optional)
- **Frontend**: React.js (planned)

## 📋 Prerequisites

- Python 3.10+
- CUDA-compatible GPU (for LLM inference)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd FinSightAI
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Backend
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the Backend
```bash
python test_backend.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Company Search
```bash
GET /api/company/search?q=Reliance
```

#### Chat with AI
```bash
POST /api/chat/ask
{
  "symbol": "RELIANCE",
  "question": "What are the main risk factors?",
  "context": "Annual report text...",
  "session_id": "optional-session-id"
}
```

#### Upload Report
```bash
POST /api/report/upload
# Multipart form with file and optional symbol
```

#### LLM Status
```bash
GET /api/llm/status
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
# Optional: HuggingFace token for gated models
HF_TOKEN=your_token_here

# Optional: Database URL
DATABASE_URL=sqlite:///./finsight.db
```

### Model Path
The LLM client expects your fine-tuned model at:
```
llm fine tune/l3_finagent_step60/l3_finagent_step60/
```

## 📖 Usage Examples

### 1. Search for Companies
```python
import requests

# Search for companies
response = requests.get("http://localhost:8000/api/company/search?q=Reliance")
companies = response.json()
print(f"Found {len(companies)} companies")
```

### 2. Ask Financial Questions
```python
# Ask about risk factors
data = {
    "symbol": "RELIANCE",
    "question": "What are the main risk factors mentioned in the annual report?",
    "context": "Annual report text content..."
}

response = requests.post("http://localhost:8000/api/chat/ask", json=data)
answer = response.json()
print(f"Answer: {answer['answer']}")
```

### 3. Upload and Parse Reports
```python
# Upload a PDF report
with open("annual_report.pdf", "rb") as f:
    files = {"file": f}
    data = {"symbol": "RELIANCE"}
    response = requests.post("http://localhost:8000/api/report/upload", 
                           files=files, data=data)
    result = response.json()
    print(f"Parsed {result['text_length']} characters")
```

## 🔍 Features in Detail

### Company Search
- Loads real NSE data from `financial_data/ind_nifty500list.csv`
- Autocomplete functionality
- Symbol and name-based search

### Document Parsing
- **PDF Support**: Uses pdfplumber and PyMuPDF for robust text extraction
- **HTML Support**: BeautifulSoup for web content parsing
- **Section Extraction**: Automatically identifies key sections (risk factors, management discussion, etc.)

### LLM Integration
- **Local Inference**: Uses your fine-tuned LLaMA-3 model
- **Prompt Engineering**: Optimized prompts for financial Q&A
- **Fallback Mode**: Graceful degradation if model isn't loaded

### Chat System
- **Session Management**: Track conversation history
- **Context Awareness**: Use uploaded/fetched reports as context
- **Multi-turn Conversations**: Support for follow-up questions

## 🚧 Development Roadmap

### Phase 1: Core Backend ✅
- [x] Company search and data management
- [x] Document parsing (PDF/HTML)
- [x] LLM integration
- [x] Basic chat functionality
- [x] Report upload/fetching

### Phase 2: Enhanced Features
- [ ] Vector database integration (Chroma/FAISS)
- [ ] Advanced scraping (Selenium/Playwright)
- [ ] Database persistence
- [ ] User authentication

### Phase 3: Frontend
- [ ] React.js frontend
- [ ] Interactive chat interface
- [ ] Company search UI
- [ ] Report upload interface

### Phase 4: Advanced Features
- [ ] Voice input (Whisper)
- [ ] Chart generation
- [ ] Sentiment analysis
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for educational and research purposes only. The information provided does not constitute financial advice. Always consult with qualified financial advisors before making investment decisions.

## 🆘 Troubleshooting

### Common Issues

1. **Model Loading Failed**
   - Ensure your fine-tuned model is in the correct directory
   - Check CUDA availability for GPU inference
   - Verify model files are complete

2. **Company Search Not Working**
   - Check if `financial_data/ind_nifty500list.csv` exists
   - Verify file permissions

3. **PDF Parsing Issues**
   - Install additional dependencies: `pip install pdfplumber pymupdf`
   - Check if PDF is password-protected

4. **API Connection Errors**
   - Ensure FastAPI server is running on port 8000
   - Check CORS settings for frontend integration

### Getting Help

- Check the API documentation at `/docs`
- Review the test script output
- Check server logs for detailed error messages

---

**FinSight AI** - Making financial analysis accessible through AI 🚀 