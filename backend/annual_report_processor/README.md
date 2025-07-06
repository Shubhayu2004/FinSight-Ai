# Annual Report Processor with FinAgent

A comprehensive system for extracting information from annual reports and interacting with your fine-tuned FinAgent LLM for financial analysis.

## 🎯 Overview

This system provides a complete pipeline for:
- **PDF Processing**: Extract text and structured data from annual report PDFs
- **Information Extraction**: Identify key sections (financial statements, management discussion, risk factors, ESG, etc.)
- **Text Processing**: Chunk and prepare text for LLM consumption
- **FinAgent Integration**: Query your fine-tuned Llama-3-8B model about annual report content
- **API Interface**: RESTful API for easy integration

## 🏗️ Architecture

```
Annual Report PDF → PDF Parser → Text Processor → FinAgent LLM → Financial Analysis
                     ↓              ↓              ↓
                Extract Text    Create Chunks   Generate Response
                Find Sections   Build Context   Return Analysis
                Get Financials  Optimize Tokens  Store History
```

## 📦 Installation

### 1. Install Dependencies

```bash
# Install core requirements for FinAgent
pip install -r requirements_annual_report.txt

# Or install individually
pip install PyMuPDF fastapi uvicorn transformers peft torch accelerate
```

### 2. Model Setup

The system is configured to use your fine-tuned FinAgent model located at:
```
llm fine tune/l3_finagent_step60/l3_finagent_step60/
```

This contains:
- `adapter_model.safetensors` - LoRA adapters
- `tokenizer.json` - Tokenizer configuration
- `adapter_config.json` - LoRA configuration
- `chat_template.jinja` - Chat template

### 3. Reports Setup

Place your annual report PDFs in the `Reports/` folder:
```
Reports/
├── AR_26456_TCS_2024_2025_A_27052025233502.pdf
├── AR_24850_RELIANCE_2023_2024_07082024143222.pdf
└── ...
```

## 🚀 Quick Start

### Basic Usage

```python
from annual_report_processor import AnnualReportProcessor

# Initialize processor with FinAgent (default)
processor = AnnualReportProcessor(llm_client_type="finagent")

# Process an annual report
result = processor.process_annual_report("Reports/TCS_Annual_Report.pdf")

# Query the report
response = processor.query_annual_report(
    pdf_path="Reports/TCS_Annual_Report.pdf",
    query="How did the company perform in North America?",
    company_name="TCS"
)

print(response['response'])
```

### API Usage

```bash
# Start the API server
cd backend
uvicorn api.annual_report_api:app --reload

# Test FinAgent model
curl -X POST "http://localhost:8000/test-finagent"

# Get model information
curl -X GET "http://localhost:8000/model-info"

# Upload a PDF
curl -X POST "http://localhost:8000/upload-pdf" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@Reports/TCS_Annual_Report.pdf"

# Query the report
curl -X POST "http://localhost:8000/query-report" \
     -H "Content-Type: application/json" \
     -d '{
       "pdf_filename": "TCS_Annual_Report.pdf",
       "query": "What was the revenue growth?",
       "company_name": "TCS"
     }'
```

## 🔧 Configuration

### FinAgent Model Configuration

```python
processor = AnnualReportProcessor(
    llm_client_type="finagent",
    llm_client_kwargs={
        "model_path": "llm fine tune/l3_finagent_step60/l3_finagent_step60",
        "device": "auto"  # or "cuda", "cpu"
    },
    max_context_tokens=4000
)
```

### Alternative LLM Clients

#### HuggingFace (Fallback)
```python
processor = AnnualReportProcessor(
    llm_client_type="huggingface",
    llm_client_kwargs={"model_name": "microsoft/DialoGPT-medium"}
)
```

#### Local LLM (Ollama)
```python
processor = AnnualReportProcessor(
    llm_client_type="local",
    llm_client_kwargs={
        "base_url": "http://localhost:11434",
        "model": "llama2"
    }
)
```

## 📊 Features

### 1. PDF Processing
- **Text Extraction**: Extract all text from PDF files
- **Section Identification**: Automatically find key sections:
  - Financial Statements
  - Management Discussion & Analysis
  - Risk Factors
  - ESG/Sustainability
  - Business Overview
  - Corporate Governance
- **Financial Data Extraction**: Extract key metrics (Revenue, PAT, EPS, etc.)

### 2. Text Processing
- **Smart Chunking**: Split large texts into manageable chunks
- **Token Optimization**: Stay within LLM token limits
- **Context Building**: Create relevant context based on user queries
- **Overlap Management**: Maintain context continuity between chunks

### 3. FinAgent Integration
- **Fine-tuned Model**: Uses your Llama-3-8B + LoRA adapters
- **Specialized Prompts**: Financial analysis-focused prompts
- **Chat Template**: Proper formatting for the model
- **Conversation History**: Track and manage query history
- **Error Handling**: Robust error handling and fallbacks

### 4. API Features
- **File Upload**: Upload PDF files via REST API
- **Batch Processing**: Process multiple reports at once
- **Query Interface**: Natural language queries about reports
- **Model Information**: Get details about loaded FinAgent model
- **Statistics**: Processing statistics and system health
- **File Management**: List, delete uploaded files

## 📝 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-pdf` | Upload a PDF file |
| POST | `/process-report` | Process an uploaded PDF |
| POST | `/query-report` | Query the FinAgent about a report |
| POST | `/batch-process` | Process all PDFs in upload directory |

### FinAgent Specific

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/model-info` | Get FinAgent model information |
| POST | `/test-finagent` | Test FinAgent with sample data |

### Information Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/available-sections/{pdf_filename}` | Get available sections |
| GET | `/financial-summary/{pdf_filename}` | Get financial summary |
| GET | `/conversation-history` | Get query history |
| GET | `/stats` | Get processing statistics |
| GET | `/uploaded-files` | List uploaded files |

### Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| DELETE | `/conversation-history` | Clear conversation history |
| DELETE | `/uploaded-files/{pdf_filename}` | Delete uploaded file |
| GET | `/health` | Health check |

## 🔍 Usage Examples

### Example 1: Process TCS Report
```python
# Process and analyze TCS annual report
processor = AnnualReportProcessor(llm_client_type="finagent")

# Process the report
result = processor.process_annual_report("Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf")

# Get financial summary
financial_data = processor.get_financial_summary("Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf")
print(f"Revenue: {financial_data.get('revenue', 'N/A')}")

# Query about performance
response = processor.query_annual_report(
    "Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf",
    "How did TCS perform in the US market?",
    "TCS"
)
print(response['response'])
```

### Example 2: Batch Process All Reports
```python
# Process all reports in the Reports folder
processor = AnnualReportProcessor(llm_client_type="finagent")

# Process all PDFs in the directory
results = processor.batch_process_reports("Reports/")

for result in results:
    if result.get('success'):
        print(f"✓ {result['file_name']}: {result['total_chunks']} chunks")
    else:
        print(f"✗ {result['file_name']}: {result.get('error')}")
```

### Example 3: Advanced Financial Analysis
```python
# Complex financial analysis with FinAgent
queries = [
    "What were the main drivers of revenue growth?",
    "How does the company's debt position compare to industry peers?",
    "What are the key risks mentioned in the management discussion?",
    "What ESG initiatives were highlighted in the report?"
]

for query in queries:
    response = processor.query_annual_report(
        "Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf",
        query,
        "TCS"
    )
    print(f"Q: {query}")
    print(f"A: {response['response']}\n")
```

## 🛠️ Development

### Running Examples
```bash
# Run the example usage script
cd backend/annual_report_processor
python example_usage.py
```

### Testing FinAgent
```bash
# Test the FinAgent model
curl -X POST "http://localhost:8000/test-finagent"

# Get model information
curl -X GET "http://localhost:8000/model-info"
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Formatting
```bash
# Install formatting tools
pip install black flake8

# Format code
black annual_report_processor/

# Check code quality
flake8 annual_report_processor/
```

## 📁 Project Structure

```
annual_report_processor/
├── __init__.py              # Package initialization
├── pdf_parser.py           # PDF text extraction and parsing
├── text_processor.py       # Text chunking and context building
├── llm_client.py          # LLM client implementations (includes FinAgent)
├── processor.py           # Main orchestrator
├── example_usage.py       # Usage examples with actual reports
└── README.md              # This file

api/
└── annual_report_api.py   # FastAPI endpoints

Reports/                   # Your annual report PDFs
├── AR_26456_TCS_2024_2025_A_27052025233502.pdf
└── AR_24850_RELIANCE_2023_2024_07082024143222.pdf

llm fine tune/
└── l3_finagent_step60/   # Your fine-tuned FinAgent model
    └── l3_finagent_step60/
        ├── adapter_model.safetensors
        ├── tokenizer.json
        ├── adapter_config.json
        └── chat_template.jinja

cache/                     # Cached processed data
uploads/                   # Uploaded PDF files
```

## 🔧 Troubleshooting

### Common Issues

1. **FinAgent Model Not Loading**
   ```bash
   # Check model path
   ls -la "llm fine tune/l3_finagent_step60/l3_finagent_step60/"
   
   # Install missing dependencies
   pip install transformers peft torch accelerate
   ```

2. **CUDA Out of Memory**
   ```python
   # Use CPU instead
   processor = AnnualReportProcessor(
       llm_client_type="finagent",
       llm_client_kwargs={"device": "cpu"}
   )
   ```

3. **PDF Processing Fails**
   - Ensure PDF is not password-protected
   - Check if PDF contains extractable text (not scanned images)
   - Verify file path is correct

4. **Model Path Issues**
   ```python
   # Specify exact model path
   processor = AnnualReportProcessor(
       llm_client_type="finagent",
       llm_client_kwargs={
           "model_path": "absolute/path/to/llm fine tune/l3_finagent_step60/l3_finagent_step60"
       }
   )
   ```

### Performance Optimization

1. **Memory Management**: Use CPU if GPU memory is insufficient
2. **Caching**: Processed data is automatically cached
3. **Batch Processing**: Process multiple files efficiently
4. **Token Management**: Optimize context size for your model

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example usage
3. Test the FinAgent model: `curl -X POST "http://localhost:8000/test-finagent"`
4. Check the API documentation at `/docs` when running the server
5. Open an issue on GitHub 