import edge_tts
import uuid
import os
import asyncio

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio_cache")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Available voices (a good subset for different genders/ages)
AVAILABLE_VOICES = {
    # Male voices
    "en-US-GuyNeural": "Guy (US Male, warm)",
    "en-US-DavisNeural": "Davis (US Male, deep)",
    "en-GB-RyanNeural": "Ryan (British Male)",
    "en-IN-PrabhatNeural": "Prabhat (Indian Male)",
    "en-AU-WilliamNeural": "William (Australian Male)",
    # Female voices
    "en-US-JennyNeural": "Jenny (US Female)",
    "en-US-AriaNeural": "Aria (US Female, expressive)",
    "en-GB-SoniaNeural": "Sonia (British Female)",
    "en-IN-NeerjaNeural": "Neerja (Indian Female)",
    "en-AU-NatashaNeural": "Natasha (Australian Female)",
    # Elderly-sounding
    "en-US-TonyNeural": "Tony (US Male, older)",
    "en-US-JasonNeural": "Jason (US Male, calm)",
}


async def generate_speech(text: str, voice_id: str = "en-US-GuyNeural") -> str:
    """Generate speech audio using Edge TTS with retry logic. Returns the file path."""
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice_id)
            await communicate.save(filepath)
            print(f"🔊 Generated speech: {filename} ({voice_id})")
            return filepath
        except Exception as e:
            print(f"⚠️ TTS attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                print(f"❌ TTS failed after {max_retries} attempts")
                raise


def get_available_voices() -> dict:
    """Return the list of available voices."""
    return AVAILABLE_VOICES
