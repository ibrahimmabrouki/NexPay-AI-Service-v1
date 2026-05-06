from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatRequest(BaseModel):
    user_id: str
    question: str
    history: List[Dict] = []
    summary: str = ""

class ChatResponse(BaseModel):
    answer: str