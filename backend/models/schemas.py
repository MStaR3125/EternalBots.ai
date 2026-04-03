from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─── Persona ───────────────────────────────────────────────
class PersonaCreate(BaseModel):
    name: str
    relationship: str = ""
    description: str = ""
    voice_id: str = "en-US-GuyNeural"


class PersonaResponse(BaseModel):
    id: int
    name: str
    relationship: str
    description: str
    photo_path: str
    voice_id: str
    created_at: str
    facts: List[str] = []
    traits: List[str] = []


# ─── Chat ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    persona_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    new_traits_learned: List[str] = []


# ─── TTS ───────────────────────────────────────────────────
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-GuyNeural"
    persona_id: Optional[int] = None


class TTSResponse(BaseModel):
    audio_url: str
    video_url: Optional[str] = None


# ─── Facts & Traits ───────────────────────────────────────
class FactCreate(BaseModel):
    persona_id: int
    fact_text: str
    source: str = "manual"


class TraitCreate(BaseModel):
    persona_id: int
    trait_text: str
    learned_from: str = "conversation"
