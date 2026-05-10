from fastapi import APIRouter, UploadFile, File
import shutil
import os

from services.speech_to_text import transcribe_audio
from services.llm import ask_ollama

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, audio.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # 1. Speech → text
    text = transcribe_audio(file_path)

    # 2. Text → AI (Ollama)
    answer = ask_ollama(text)

    return {
        "transcription": text,
        "response": answer
    }
