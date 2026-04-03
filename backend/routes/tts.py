from fastapi import APIRouter
from fastapi.responses import FileResponse
from models.schemas import TTSRequest, TTSResponse
from services.voice import generate_speech, get_available_voices
import os
import traceback

router = APIRouter(prefix="/api/tts", tags=["Text-to-Speech"])


@router.post("", response_model=TTSResponse)
async def text_to_speech(req: TTSRequest):
    """Convert text to speech, optionally apply voice cloning, and optionally generate D-ID lip-sync."""
    filepath = None
    is_elevenlabs = False
    
    if req.persona_id:
        try:
            from services.voice_clone import clone_voice_elevenlabs, ELEVENLABS_API_KEY
            if ELEVENLABS_API_KEY:
                print(f"🎙️ Using ElevenLabs API to generate cloned voice for persona {req.persona_id}...")
                filepath = clone_voice_elevenlabs(req.text, req.persona_id)
                if filepath:
                    is_elevenlabs = True
        except Exception as e:
            print(f"⚠️ ElevenLabs voice clone skipped: {e}")
            traceback.print_exc()

    # Fallback to Edge TTS if ElevenLabs isn't used or failed
    if not filepath:
        filepath = await generate_speech(req.text, req.voice_id)
        
        # Try OpenVoice cloning if enabled
        if req.persona_id:
            try:
                from services.voice_clone import clone_voice_openvoice
                filepath = clone_voice_openvoice(filepath, req.persona_id)
            except Exception as e:
                print(f"⚠️ OpenVoice clone skipped: {e}")
        
        try:
            from services.lipsync import generate_did_video
            print(f"🎬 Attempting D-ID lip-sync for persona {req.persona_id}...")
            video_url = generate_did_video(filepath, req.persona_id)
            if video_url:
                print(f"✅ D-ID video URL: {video_url[:80]}...")
            else:
                print("⚠️ D-ID returned no video URL")
        except Exception as e:
            print(f"⚠️ D-ID lip-sync skipped: {e}")
            traceback.print_exc()
        
    filename = os.path.basename(filepath)
    return {"audio_url": f"/audio/{filename}", "video_url": video_url}


@router.get("/voices")
async def list_voices():
    """List available TTS voices."""
    return get_available_voices()


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve an audio file."""
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio_cache")
    filepath = os.path.join(audio_dir, filename)

    if not os.path.exists(filepath):
        return {"error": "Audio file not found"}

    return FileResponse(filepath, media_type="audio/mpeg")
