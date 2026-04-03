import requests
import time
import os
import json

API = "http://localhost:8000"
DATA_DIR = r"c:\Users\micro\OneDrive\Desktop\ETERNAL_BOTS_AI\v2\SampleData"

def test_clone():
    print("=" * 60)
    print("ETERNALBOTS v2 — CUSTOM CLONE TEST")
    print("=" * 60)

    # 1. Create persona
    print("\n--- STEP 1: Create Custom Persona ---")
    res = requests.post(f"{API}/api/persona", json={
        "name": "Custom Persona",
        "description": "A custom user-provided persona clone",
        "relationship": "Friend",
        "voice_id": "en-US-GuyNeural"
    })
    
    if res.status_code != 200:
        print(f"❌ CREATE FAILED: {res.text}")
        return
        
    pid = res.json()["id"]
    print(f"✅ Created persona ID={pid}")

    # 2. Upload photo
    print("\n--- STEP 2: Upload photo ---")
    photo = os.path.join(DATA_DIR, "photo.jpg")
    print(f"Checking for photo at: {photo}")
    if os.path.exists(photo):
        with open(photo, "rb") as f:
            res = requests.post(f"{API}/api/persona/{pid}/upload",
                                files={"file": ("photo.jpg", f, "image/jpeg")})
        print(f"✅ Photo upload: {res.status_code}")
    else:
        print(f"⚠️ Photo not found")

    # 3. Upload audio reference
    print("\n--- STEP 3: Upload audio reference ---")
    audio = os.path.join(DATA_DIR, "reference_audio.wav")
    print(f"Checking for audio at: {audio}")
    if os.path.exists(audio):
        with open(audio, "rb") as f:
            res = requests.post(f"{API}/api/persona/{pid}/upload",
                                files={"file": ("reference_audio.wav", f, "audio/wav")})
        print(f"✅ Audio upload: {res.status_code}")
    else:
        print(f"⚠️ Audio not found")

    # 4. Upload facts text
    print("\n--- STEP 4: Upload facts text ---")
    facts_file = os.path.join(DATA_DIR, "facts.txt")
    print(f"Checking for facts at: {facts_file}")
    if os.path.exists(facts_file):
        with open(facts_file, "rb") as f:
            res = requests.post(f"{API}/api/persona/{pid}/upload",
                                files={"file": ("facts.txt", f, "text/plain")})
        print(f"✅ Facts text upload: {res.status_code}")
    else:
        print(f"⚠️ Facts not found")

    # Wait for background fact extraction
    print("\n--- Waiting 15s for LLM fact extraction... ---")
    time.sleep(15)

    # 5. Verify persona data
    print("\n--- STEP 5: Verify extracted memory ---")
    res = requests.get(f"{API}/api/persona/{pid}")
    data = res.json()
    print(f"  Facts extracted: {len(data['facts'])}")
    if len(data['facts']) > 0:
        print("  Sample facts:")
        for f in data['facts'][:3]:
            print(f"    - {f['fact_text']}")

    # 6. Test Chat & TTS Pipeline
    print("\n--- STEP 6: Test Voice Clone & Chat pipeline ---")
    res = requests.post(f"{API}/api/chat", json={
        "persona_id": pid,
        "message": "Hello! How are you doing today?"
    })
    chat_data = res.json()
    print(f"  LLM Reply: {chat_data['reply'][:200]}")

    print("\n--- STEP 7: Test ElevenLabs & D-ID Lip Sync ---")
    try:
        print("  Generating TTS (this will trigger ElevenLabs and D-ID)...")
        start = time.time()
        res = requests.post(f"{API}/api/tts", json={
            "text": chat_data['reply'],
            "voice_id": "en-US-GuyNeural",
            "persona_id": pid
        }, timeout=120)
        
        if res.status_code == 200:
            tts_data = res.json()
            print(f"  Time taken: {time.time() - start:.1f}s")
            print(f"  ✅ Audio URL (ElevenLabs): {tts_data.get('audio_url', 'MISSING')}")
            print(f"  ✅ Video URL (D-ID): {tts_data.get('video_url', 'MISSING')}")
        else:
            print(f"  ❌ TTS Error: {res.status_code} {res.text}")
    except requests.exceptions.ReadTimeout:
        print("  ❌ TTS timed out after 120s (D-ID might be slow)")
    except Exception as e:
        print(f"  ❌ TTS exception: {e}")

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE ✅")
    print(f"Open Frontend: http://localhost:5173 to test visually.")
    print("=" * 60)

if __name__ == "__main__":
    test_clone()
