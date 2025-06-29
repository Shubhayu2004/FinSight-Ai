from fastapi import APIRouter, Body
from typing import Dict

router = APIRouter()

@router.post("/generate")
def generate_answer(
    context: str = Body(...),
    question: str = Body(...)
) -> Dict:
    # TODO: Call local fine-tuned LLM
    return {
        "answer": f"Stub: LLM would answer '{question}' given the provided context.",
        "raw": None
    } 