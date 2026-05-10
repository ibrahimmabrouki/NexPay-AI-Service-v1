from fastapi import FastAPI
from routes.chat import router as chat_router
import routes.summarize_memory as summarize_memory_router
from routes.voice_chat import router as speech_router

app = FastAPI()

app.include_router(chat_router, prefix="/api")
app.include_router(summarize_memory_router.router, prefix="/api")
app.include_router(speech_router, prefix="/api")
