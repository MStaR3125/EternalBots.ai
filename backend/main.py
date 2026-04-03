from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db.database import init_db
from routes import persona, chat, tts
import os

app = FastAPI(
    title="EternalBots.ai API",
    description="Digitally preserve the conversational essence of your loved ones",
    version="2.0.0",
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_cache")
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# Include routers
app.include_router(persona.router)
app.include_router(chat.router)
app.include_router(tts.router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    print("🚀 EternalBots.ai v2.0 API is running!")
    print("📖 Docs at: http://localhost:8000/docs")


@app.get("/")
async def root():
    return {
        "name": "EternalBots.ai",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }
