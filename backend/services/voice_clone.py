import os
import uuid
from dotenv import load_dotenv
from db.database import get_db

load_dotenv()

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio_cache")
os.makedirs(AUDIO_DIR, exist_ok=True)

OPENVOICE_ENABLED = os.getenv("OPENVOICE_ENABLED", "false").lower() == "true"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

def get_persona_reference_audio(persona_id: int):
    """Get the first uploaded audio file for a persona to use as reference."""
    conn = get_db()
    audio_file = conn.execute(
        "SELECT file_path FROM uploaded_files WHERE persona_id = ? AND file_type = 'audio' ORDER BY created_at ASC LIMIT 1",
        (persona_id,)
    ).fetchone()
    conn.close()
    
    if audio_file and os.path.exists(audio_file["file_path"]):
        return audio_file["file_path"]
    return None

def store_elevenlabs_voice_id(persona_id: int, voice_id: str):
    """Store the ElevenLabs Voice ID for reuse."""
    conn = get_db()
    # In a real system, you'd add this column. Here we just update voice_id if it's currently using an Edge TTS voice.
    conn.execute("UPDATE personas SET voice_id = ? WHERE id = ?", (voice_id, persona_id))
    conn.commit()
    conn.close()

def clone_voice_elevenlabs(text: str, persona_id: int) -> str:
    """Clones a voice using ElevenLabs Instant Voice Cloning."""
    if not ELEVENLABS_API_KEY:
        return None
        
    reference_audio_path = get_persona_reference_audio(persona_id)
    if not reference_audio_path:
        print(f"⚠️ No reference audio found for persona {persona_id}. Skipping ElevenLabs clone.")
        return None

    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        conn = get_db()
        persona = conn.execute("SELECT name, voice_id FROM personas WHERE id = ?", (persona_id,)).fetchone()
        conn.close()
        
        persona_name = persona["name"] if persona else f"Persona_{persona_id}"
        voice_id = persona["voice_id"] if persona else ""
        
        # If the voice_id is an Edge TTS one (e.g. "en-US..."), we need to create the ElevenLabs clone first
        if not voice_id or len(voice_id) != 21: # ElevenLabs IDs are typically 21 chars Base58
            print(f"🎙️ Creating ElevenLabs Instant Voice Clone for {persona_name}...")
            voice = client.voices.add(
                name=f"{persona_name} Clone",
                description=f"Cloned voice for {persona_name}",
                files=[open(reference_audio_path, 'rb')]
            )
            voice_id = voice.voice_id
            print(f"✅ Created ElevenLabs Voice ID: {voice_id}")
            store_elevenlabs_voice_id(persona_id, voice_id)
            
        print(f"🔊 Generating speech with ElevenLabs Voice ID: {voice_id}...")
        audio_generator = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
        
        out_filename = f"el_{uuid.uuid4().hex}.mp3"
        out_filepath = os.path.join(AUDIO_DIR, out_filename)
        
        with open(out_filepath, "wb") as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)
                    
        print(f"✅ ElevenLabs audio generated: {out_filename}")
        return out_filepath
        
    except Exception as e:
        print(f"❌ ElevenLabs cloning error: {e}")
        return None


def clone_voice_openvoice(base_audio_path: str, persona_id: int) -> str:
    """Clones a voice using OpenVoice v2 Tone Color Converter."""
    if not OPENVOICE_ENABLED:
        return base_audio_path
        
    reference_audio_path = get_persona_reference_audio(persona_id)
    if not reference_audio_path:
        print(f"⚠️ No reference audio found for persona {persona_id}. Skipping OpenVoice clone.")
        return base_audio_path

    out_filename = f"clone_{uuid.uuid4().hex}.wav"
    out_filepath = os.path.join(AUDIO_DIR, out_filename)
    
    try:
        from openvoice import se_extractor
        from openvoice.api import ToneColorConverter
        import torch

        print("🔄 Applying OpenVoice v2 cloning...")
        ckpt_converter = 'checkpoints_v2/converter'
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
        tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

        target_se, _ = se_extractor.get_se(reference_audio_path, tone_color_converter, target_dir='processed', vad=False)
        source_se, _ = se_extractor.get_se(base_audio_path, tone_color_converter, target_dir='processed', vad=False)

        tone_color_converter.convert(
            audio_src_path=base_audio_path, 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=out_filepath,
            message="@EternalBots"
        )
        print(f"✅ Voice cloned successfully: {out_filename}")
        return out_filepath
        
    except ImportError:
        print("❌ OpenVoice package not found on this Python version.")
        return base_audio_path
    except Exception as e:
        print(f"❌ Voice cloning error: {e}")
        return base_audio_path
