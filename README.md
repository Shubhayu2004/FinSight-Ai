# AI Finance Agent

An intelligent financial analysis system that uses FinGPT with PEFT adapter to analyze annual reports and provide financial insights.

## 🚀 Features

- **FinGPT Integration**: Uses Llama-2-7b-chat-hf with FinGPT PEFT adapter for specialized financial analysis
- **Fallback Support**: Automatically falls back to open-access models if Llama-2 access is not approved
- **Annual Report Processing**: Extract and analyze financial data from PDF annual reports
- **Intelligent Queries**: Ask questions about company performance, financial metrics, and business insights
- **Web Interface**: Modern FastAPI backend with frontend interface
- **Caching System**: Efficient caching for processed reports

## 📋 Requirements

- Python 3.8+
- CUDA-capable GPU (recommended 4GB+ VRAM for fallback, 8GB+ for Llama-2)
- 16GB+ RAM
- 10GB+ free disk space

## 🔐 Model Access

### Llama-2 Model (Recommended)
The system is designed to use Llama-2-7b-chat-hf with FinGPT PEFT adapter for optimal performance. However, this requires access approval from Meta:

1. **Request Access**: Visit [HuggingFace Llama-2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
2. **Submit Request**: Click "Request access" and fill out the form
3. **Wait for Approval**: Meta typically responds within 24-48 hours
4. **Login**: Use `huggingface-cli login` after approval

### Fallback Model (Immediate Use)
While waiting for Llama-2 access, the system automatically uses Microsoft's DialoGPT-medium, which is open-access and provides good baseline performance.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-finance-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download models locally (recommended)**:
   ```bash
   # Download fallback model for immediate use
   python utils/download_fallback_model.py
   
   # Or download all models (including PEFT adapters)
   python utils/download_models.py
   ```

4. **Test the system**:
   ```bash
   python utils/test_model_loading.py
   ```

## 🚀 Local Model Caching

To reduce access time and enable offline usage, the system supports local model caching:

### Quick Setup
```bash
# Download fallback model (fast, ~1GB)
python utils/download_fallback_model.py

# Download all models (slower, ~15GB total)
python utils/download_models.py
```

### Cache Management
```bash
# View cache information
python utils/download_models.py --info

# Force re-download
python utils/download_models.py --force

# Clean up cache
python utils/cleanup_cache.py
```

### Cache Location
- **Default**: `./models/` directory in project root
- **Configurable**: Set in `backend/config.py`
- **Environment**: Automatically sets `HF_HOME` and `TRANSFORMERS_CACHE`

## 🧪 Testing

Run the test script to verify model loading:

```bash
python utils/test_model_loading.py
```

This will:
- Test the fallback model (should work immediately)
- Try to load Llama-2 model (if access is approved)
- Display model information and test generation
- Provide clear feedback about access status

### Expected Output

**With local cache:**
```
✅ Fallback model loaded successfully! (from local cache)
⚠️  Llama-2 model not available (access not approved yet)
```

**Without local cache:**
```
✅ Fallback model loaded successfully! (downloaded)
⚠️  Llama-2 model not available (access not approved yet)
```

## 🗂️ Project Structure

```
AI-finance-agent/
├── backend/
│   ├── annual_report_processor/
│   │   ├── llm_client.py          # FinGPT LLM client with PEFT
│   │   ├── processor.py           # Annual report processor
│   │   ├── pdf_parser.py          # PDF parsing utilities
│   │   └── text_processor.py      # Text processing utilities
│   ├── config.py                  # Configuration settings
│   └── api/                       # FastAPI endpoints
├── utils/                         # Utility scripts
│   ├── test_model_loading.py      # Model testing script
│   ├── download_fallback_model.py # Quick fallback model download
│   ├── download_models.py         # Full model downloader
│   └── cleanup_cache.py           # Cache cleanup utility
├── models/                        # Local model cache (created by download scripts)
├── Reports/                       # Annual report PDFs
├── frontend/                      # Web interface
└── requirements.txt               # Python dependencies
```

## 🔧 Configuration

The model configuration is in `backend/config.py`:

```python
# Model configuration
FINGPT_MODEL_NAME = "microsoft/DialoGPT-medium"  # Fallback model
LLAMA2_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"  # Requires access
PEFT_ADAPTER_NAME = "FinGPT/fingpt-forecaster_dow30_llama2-7b_lora"

# Local cache configuration
MODEL_CACHE_DIR = "models"  # Local cache directory
USE_LOCAL_CACHE = True      # Enable local caching
```

## 🧹 Maintenance

### Cache Management

**View cache usage:**
```bash
python utils/download_models.py --info
```

**Clean up cache files:**
```bash
# View current cache usage
python utils/cleanup_cache.py --info

# Clean up all cache files
python utils/cleanup_cache.py
```

**Download specific models:**
```bash
# Download only fallback model
python utils/download_fallback_model.py

# Download specific models
python utils/download_models.py --models microsoft/DialoGPT-medium

# Download PEFT adapters
python utils/download_models.py --adapters FinGPT/fingpt-forecaster_dow30_llama2-7b_lora
```

### Model Information

**Fallback Model:**
- **Model**: Microsoft DialoGPT-medium
- **Parameters**: ~345M
- **Memory**: ~2GB VRAM
- **Cache Size**: ~1GB
- **Access**: Open (no approval needed)

**Llama-2 Model (with PEFT):**
- **Base Model**: Llama-2-7b-chat-hf (7B parameters)
- **PEFT Adapter**: FinGPT Dow30 forecaster LoRA
- **Specialization**: Financial forecasting and analysis
- **Memory**: ~8GB VRAM recommended
- **Cache Size**: ~15GB total
- **Access**: Requires Meta approval

## 🚀 Usage

1. **Download models locally** (recommended):
   ```bash
   python utils/download_fallback_model.py
   ```

2. **Start the backend server**:
   ```bash
   cd backend
   uvicorn api.main:app --reload
   ```

3. **Upload annual reports** through the web interface

4. **Ask questions** about the financial data

## 📊 Supported Models

- **FinGPT with PEFT**: Primary model for financial analysis (requires Llama-2 access)
- **Fallback Model**: Open-access alternative for immediate use
- **HuggingFace Models**: Alternative local models
- **Local LLM Services**: Ollama, LM Studio, etc.

## 🔍 Troubleshooting

### Common Issues

1. **Out of Memory**: 
   - Fallback model: Reduce to 4GB VRAM
   - Llama-2 model: Reduce to 8GB VRAM or use CPU
2. **Model Loading Failed**: Check internet connection and dependencies
3. **CUDA Errors**: Update NVIDIA drivers and PyTorch
4. **Access Denied**: Request Llama-2 access from Meta
5. **Slow Loading**: Download models locally using the download scripts

### Dependencies

Key packages:
- `transformers`: HuggingFace model loading
- `torch`: PyTorch for model inference
- `peft`: Parameter-efficient fine-tuning
- `accelerate`: Model optimization

### Getting Llama-2 Access

1. Go to [HuggingFace Llama-2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
2. Click "Request access"
3. Fill out the form with your use case
4. Wait for email approval
5. Run `huggingface-cli login` with your token

### Performance Optimization

**For faster loading:**
1. Download models locally: `python utils/download_fallback_model.py`
2. Use SSD storage for cache directory
3. Ensure sufficient RAM (16GB+ recommended)
4. Use CUDA if available

**For memory optimization:**
1. Use fallback model for testing (lower memory)
2. Enable model quantization in config
3. Use CPU inference if GPU memory is limited

## 📝 License

This project is for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test script output
3. Check system requirements
4. Verify Llama-2 access status
5. Open an issue with detailed error information 