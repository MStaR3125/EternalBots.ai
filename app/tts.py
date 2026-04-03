"""
tts.py – Text-to-Speech for EternalBots Pope Francis

Tier 1 (primary): XTTS-v2 voice cloning on GPU
  - Uses data/pope_ref.wav as the voice reference
  - Clones Pope Francis's actual voice in both English and Hindi
  - ~5-15 seconds on RTX 3050

Tier 2 (fallback): edge-tts
  - en-GB-RyanNeural for English, hi-IN-MadhurNeural for Hindi
  - Instant generation, no GPU, requires internet

Tier 3 (offline fallback): silent audio placeholder
"""

import uuid
import pathlib
import os
import asyncio
import re
from functools import lru_cache
import soundfile as sf
import numpy as np
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

USE_VOICE_CLONING = os.getenv("USE_VOICE_CLONING", "true").lower() == "true"
TTS_ENGLISH_VOICE = os.getenv("TTS_ENGLISH_VOICE", "en-GB-RyanNeural")
TTS_HINDI_VOICE = os.getenv("TTS_HINDI_VOICE", "hi-IN-MadhurNeural")

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_WAV = os.path.join(_BASE, "data", "pope_ref.wav")

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------
_HINDI_WORDS = {
    "aap", "main", "hain", "hai", "kya", "kaise", "mujhe", "tumhe", "tum",
    "yeh", "woh", "nahin", "nahi", "bahut", "accha", "theek", "shukriya",
    "dhanyawad", "namaste", "ji", "bhai", "dost", "pyar", "pyaar", "kal",
    "aaj", "bolo", "bata", "samajh", "madad", "baar", "log", "duniya",
}

def detect_language(text: str) -> str:
    """Returns 'hi' for Hindi/Hinglish, 'en' for English."""
    # Devanagari Unicode block
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    words = set(re.findall(r"\b\w+\b", text.lower()))
    if len(words & _HINDI_WORDS) >= 2:
        return "hi"
    return "en"


# ---------------------------------------------------------------------------
# Tier 1: XTTS-v2 voice cloning
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _load_xtts():
    if not USE_VOICE_CLONING:
        return None
    try:
        import torch
        from TTS.api import TTS
        import warnings
        warnings.filterwarnings("ignore")

        use_gpu = torch.cuda.is_available()
        print(f"Loading XTTS-v2 model ({'GPU' if use_gpu else 'CPU'})...")

        # Patch torch.load for weights_only compatibility
        _orig = torch.load
        def _patched(*a, **kw):
            kw.setdefault("weights_only", False)
            return _orig(*a, **kw)
        torch.load = _patched
        try:
            tts = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                progress_bar=True,
                gpu=use_gpu,
            )
        finally:
            torch.load = _orig

        print(f"[OK] XTTS-v2 loaded {'(GPU)' if use_gpu else '(CPU)'}")
        return tts
    except Exception as e:
        print(f"[WARN] XTTS-v2 unavailable: {e}")
        return None


def _speak_xtts(text: str, lang: str, out_path: str) -> bool:
    """Try XTTS-v2 voice cloning. Returns True on success."""
    tts = _load_xtts()
    if tts is None:
        return False
    if not os.path.exists(REF_WAV):
        print(f"[WARN] Voice reference not found: {REF_WAV}")
        return False
    try:
        wav = tts.tts(text=text, speaker_wav=[REF_WAV], language=lang)
        sf.write(out_path, wav, 24000)
        print(f"[OK] XTTS-v2 voice clone: {os.path.basename(out_path)}")
        return True
    except Exception as e:
        print(f"[WARN] XTTS-v2 generation failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Tier 2: edge-tts fallback
# ---------------------------------------------------------------------------
async def _edge_generate(text: str, voice: str, out_path: str):
    import edge_tts
    comm = edge_tts.Communicate(text, voice)
    await comm.save(out_path)


def _speak_edge(text: str, lang: str, out_path: str) -> bool:
    """edge-tts fallback. Returns True on success."""
    try:
        import edge_tts  # noqa: F401 – just test import
    except ImportError:
        print("[WARN] edge-tts not installed")
        return False

    voice = TTS_HINDI_VOICE if lang == "hi" else TTS_ENGLISH_VOICE
    # edge-tts outputs mp3; we need wav for avatar/SadTalker
    mp3_path = out_path.replace(".wav", ".mp3")
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_edge_generate(text, voice, mp3_path))
        loop.close()

        # Convert mp3 → wav
        try:
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-ar", "24000", out_path],
                capture_output=True, check=True
            )
            os.remove(mp3_path)
        except Exception:
            # ffmpeg not available — rename mp3 → wav (wav player can still play it)
            os.rename(mp3_path, out_path)

        print(f"[OK] edge-tts ({voice}): {os.path.basename(out_path)}")
        return True
    except Exception as e:
        print(f"[WARN] edge-tts failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Tier 3: silent audio placeholder
# ---------------------------------------------------------------------------
def create_silent_audio(text: str) -> str:
    pathlib.Path("tmp").mkdir(exist_ok=True)
    duration = max(2, len(text.split()) * 0.5)
    samples = int(duration * 24000)
    audio = np.random.normal(0, 0.001, samples).astype(np.float32)
    path = f"tmp/{uuid.uuid4().hex}.wav"
    sf.write(path, audio, 24000)
    print(f"[WARN] Using silent audio placeholder: {os.path.basename(path)}")
    return path


# ---------------------------------------------------------------------------
# Public API — same signature as before
# ---------------------------------------------------------------------------
def speak(text: str) -> str:
    """Generate speech and return path to the wav file in tmp/."""
    pathlib.Path("tmp").mkdir(exist_ok=True)
    out = f"tmp/{uuid.uuid4().hex}.wav"

    lang = detect_language(text)
    print(f"[TTS] Detected language: {'Hindi/Hinglish' if lang == 'hi' else 'English'}")

    # Tier 1 — XTTS-v2 voice cloning
    if _speak_xtts(text, lang, out):
        return out

    # Tier 2 — edge-tts
    if _speak_edge(text, lang, out):
        return out

    # Tier 3 — silent placeholder
    return create_silent_audio(text)
