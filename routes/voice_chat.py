from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os

from services.speech_to_text import transcribe_audio
from schemas.chat_schema import ChatResponse
from services.rag_pipline import rag_pipeline

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/voice-chat", response_model=ChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    summary: str = Form(None),
    history: str = Form(None)
):
    file_path = os.path.join(UPLOAD_DIR, audio.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    text = transcribe_audio(file_path)

    import json
    history = json.loads(history) if history else []
    answer = rag_pipeline(
        user_id=user_id,
        question=text,
        history=history,
        summary=summary
    )

    return ChatResponse(question=text, answer=answer)
