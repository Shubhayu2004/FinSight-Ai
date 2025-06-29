from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.company import router as company_router
from api.report import router as report_router
from api.chat import router as chat_router
from api.llm import router as llm_router

app = FastAPI(title="FinSight AI Backend", version="0.1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(company_router, prefix="/api/company", tags=["Company"])
app.include_router(report_router, prefix="/api/report", tags=["Report"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(llm_router, prefix="/api/llm", tags=["LLM"])

@app.get("/")
def root():
    return {"message": "FinSight AI backend is running."} 