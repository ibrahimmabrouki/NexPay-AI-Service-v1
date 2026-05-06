from fastapi import APIRouter, Depends
from schemas.memory_schema import MemoryRequest
from services.memory_summarizer import generate_memory_summary
from dependencies.security import verify_internal_key

router = APIRouter()


@router.post("/summarize-memory", dependencies=[Depends(verify_internal_key)])
def summarize_memory(request: MemoryRequest):
    summary = generate_memory_summary(request.messages)
    return {"summary": summary}
