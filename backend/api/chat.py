from fastapi import APIRouter, Body
from typing import Dict

router = APIRouter()

@router.post("/ask")
def ask_question(
    symbol: str = Body(...),
    question: str = Body(...),
    context: str = Body(None)
) -> Dict:
    # TODO: Integrate with LLM and retrieval
    return {
        "answer": f"Stub: This would answer '{question}' for {symbol}.",
        "references": [],
        "charts": None
    } 