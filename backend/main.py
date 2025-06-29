from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Import the new modular API routes
from api.company import router as company_router
from api.reports import router as reports_router
from api.technical import router as technical_router
from api.chat import router as chat_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FinSight AI Backend",
    description="Financial investment report analyzer for Indian stocks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(company_router)
app.include_router(reports_router)
app.include_router(technical_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FinSight AI Backend API",
        "version": "1.0.0",
        "description": "Financial investment report analyzer for Indian stocks",
        "endpoints": {
            "company": "/api/company",
            "reports": "/api/reports", 
            "technical": "/api/technical",
            "chat": "/api/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if required directories exist
        required_dirs = [
            "../financial_data",
            "../Company Annual report",
            "../llm fine tune"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
        
        status = {
            "status": "healthy" if not missing_dirs else "warning",
            "missing_directories": missing_dirs,
            "api_version": "1.0.0"
        }
        
        if missing_dirs:
            logger.warning(f"Missing directories: {missing_dirs}")
        
        return status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        from chatbot.manager import chatbot_manager
        from company_data.manager import company_manager
        from report_extractor.manager import report_manager
        from technical_data.manager import technical_manager
        
        status = {
            "system": "FinSight AI Backend",
            "version": "1.0.0",
            "components": {
                "company_data": {
                    "status": "active",
                    "companies_loaded": len(company_manager.companies) if hasattr(company_manager, 'companies') else 0
                },
                "report_extractor": {
                    "status": "active",
                    "download_directory": report_manager.download_dir if hasattr(report_manager, 'download_dir') else "N/A"
                },
                "technical_data": {
                    "status": "active",
                    "cache_size": len(technical_manager.cache) if hasattr(technical_manager, 'cache') else 0
                },
                "chatbot": {
                    "status": "active",
                    "active_sessions": len(chatbot_manager.sessions) if hasattr(chatbot_manager, 'sessions') else 0,
                    "llm_loaded": chatbot_manager.get_llm_status().get("llm_loaded", False)
                }
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 