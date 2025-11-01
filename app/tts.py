import uuid, pathlib, threading, os
from functools import lru_cache
import soundfile as sf

@lru_cache(maxsize=1)
def _load_tts():
    """Load TTS model with error handling"""
    try:
        import torch
        from TTS.api import TTS
        import warnings
        
        # Suppress warnings
        warnings.filterwarnings("ignore")
        
        print("Loading XTTS-v2 model for voice cloning...")
        
        # Try loading with weights_only=False to bypass the restriction
        original_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs.setdefault('weights_only', False)
            return original_load(*args, **kwargs)
        torch.load = patched_load
        
        try:
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                     progress_bar=False, gpu=False)
            print("XTTS-v2 model loaded successfully!")
            return tts
        finally:
            torch.load = original_load
            
    except ImportError as e:
        print(f"⚠️ TTS library not available (Python 3.13 compatibility issue): {e}")
        print("Using fallback silent audio generation...")
        return None
    except Exception as e:
        print(f"❌ Failed to load TTS model: {e}")
        print("Using fallback silent audio generation...")
        return None
            
    except Exception as e:
        print(f"Error loading TTS model: {e}")
        print("Falling back to silent audio generation...")
        return None

REF_WAV = "data/pope_ref.wav"

def speak(text: str) -> str:
    """Generate a wav file path for given text using XTTS-v2.
    Returns path to wav file in tmp/ directory."""
    pathlib.Path("tmp").mkdir(exist_ok=True)
    
    try:
        # Use absolute path for reference audio
        if not os.path.isabs(REF_WAV):
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ref_path = os.path.join(current_dir, REF_WAV)
        else:
            ref_path = REF_WAV
            
        print(f"Looking for Pope's voice reference at: {ref_path}")
        
        # Check if reference audio exists
        if not os.path.exists(ref_path):
            print(f"Warning: Reference audio file not found at {ref_path}")
            return create_silent_audio(text)
        
        tts = _load_tts()
        if tts is None:
            print("TTS model not available, creating silent audio")
            return create_silent_audio(text)
        
        print(f"Generating Pope Francis voice for: {text[:50]}...")
        
        # Generate speech with the Pope's voice
        wav = tts.tts(text=text, speaker_wav=[ref_path], language="en")
        
        # Save to file
        path = f"tmp/{uuid.uuid4().hex}.wav"
        sf.write(path, wav, 24000)
        
        print(f"✅ Pope Francis voice generated successfully: {path}")
        return path
        
    except Exception as e:
        print(f"Error in TTS generation: {e}")
        return create_silent_audio(text)

def create_silent_audio(text: str) -> str:
    """Create a silent audio file as fallback"""
    import numpy as np
    
    # Create silent audio (duration based on text length)
    duration = max(2, len(text.split()) * 0.5)  # ~0.5 seconds per word
    sample_rate = 24000
    samples = int(duration * sample_rate)
    
    # Generate very quiet background noise instead of complete silence
    audio = np.random.normal(0, 0.001, samples).astype(np.float32)
    
    path = f"tmp/{uuid.uuid4().hex}.wav"
    sf.write(path, audio, sample_rate)
    
    print(f"Created silent audio placeholder: {path}")
    return path
