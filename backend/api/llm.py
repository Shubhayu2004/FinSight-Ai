from fastapi import APIRouter, Body
from typing import Dict
from core.llm_client import llm_client

router = APIRouter()

@router.post("/generate")
def generate_answer(
    context: str = Body(...),
    question: str = Body(...)
) -> Dict:
    """Generate answer using the fine-tuned LLM"""
    answer = llm_client.generate_answer(context, question)
    return {
        "answer": answer,
        "raw": None
    }

@router.get("/status")
def get_llm_status() -> Dict:
    """Check if LLM is loaded and ready"""
    is_loaded = llm_client.model is not None and llm_client.tokenizer is not None
    return {
        "loaded": is_loaded,
        "device": llm_client.device,
        "model_path": llm_client.model_path
    } 