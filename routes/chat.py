from fastapi import APIRouter, Depends
from schemas.chat_schema import ChatRequest, ChatResponse
from services.rag_pipline import rag_pipeline
from dependencies.security import verify_internal_key

router = APIRouter()


@router.post("/chat-AI", response_model=ChatResponse, dependencies=[Depends(verify_internal_key)])
def chat(request: ChatRequest) -> ChatResponse:
    answer = rag_pipeline(user_id=request.user_id, question=request.question,
                          history=request.history, summary=request.summary)
    return ChatResponse(answer=answer)
