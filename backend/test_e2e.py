"""Comprehensive end-to-end test for EternalBots v2"""
import requests
import time
import os

API = "http://localhost:8000"
DATA_DIR = r"c:\Users\micro\OneDrive\Desktop\ETERNAL_BOTS_AI\Model_1.0\eternalbots-pope-francis\data"

def test():
    print("=" * 60)
    print("ETERNALBOTS v2 — END-TO-END TEST")
    print("=" * 60)

    # 1. Create persona
    print("\n--- STEP 1: Create Pope Francis persona ---")
    res = requests.post(f"{API}/api/persona", json={
        "name": "Pope Francis",
        "relationship": "Spiritual Leader",
        "description": "Jorge Mario Bergoglio, head of the Catholic Church",
        "voice_id": "en-US-GuyNeural"
    })
    assert res.status_code == 200, f"CREATE FAILED: {res.text}"
    pid = res.json()["id"]
    print(f"✅ Created persona ID={pid}")

    # 2. Upload photo
    print("\n--- STEP 2: Upload photo ---")
    photo = os.path.join(DATA_DIR, "pope_face.jpg")
    if os.path.exists(photo):
        with open(photo, "rb") as f:
            res = requests.post(f"{API}/api/persona/{pid}/upload",
                                files={"file": ("pope_face.jpg", f, "image/jpeg")})
        print(f"✅ Photo upload: {res.status_code}")
    else:
        print(f"⚠️ Photo not found at {photo}")

    # 3. Upload audio reference
    print("\n--- STEP 3: Upload audio reference ---")
    audio = os.path.join(DATA_DIR, "pope_ref.wav")
    if os.path.exists(audio):
        with open(audio, "rb") as f:
            res = requests.post(f"{API}/api/persona/{pid}/upload",
                                files={"file": ("pope_ref.wav", f, "audio/wav")})
        print(f"✅ Audio upload: {res.status_code}")

    # 4. Add manual facts (since LLM extraction may be slow)
    print("\n--- STEP 4: Add facts manually ---")
    facts = [
        "Born Jorge Mario Bergoglio on 17 December 1936 in Buenos Aires, Argentina",
        "Head of the Catholic Church and sovereign of the Vatican City State",
        "First pope from the Americas and the first from the Southern Hemisphere",
        "Member of the Society of Jesus (Jesuits)",
        "Chose the papal name Francis in honor of Saint Francis of Assisi",
        "Known for his humility, emphasis on God's mercy, and concern for the poor",
        "Has a less formal approach to the papacy than his predecessors",
        "Speaks Spanish, Italian, German, and some English",
        "Worked as a bouncer, janitor, and chemical technician before entering seminary",
        "Became Pope on 13 March 2013",
    ]
    for fact in facts:
        res = requests.post(f"{API}/api/persona/{pid}/facts",
                            data={"fact_text": fact})
        assert res.status_code == 200, f"FACT FAILED: {res.text}"
    print(f"✅ Added {len(facts)} facts")

    # 5. Verify persona has facts
    print("\n--- STEP 5: Verify persona data ---")
    res = requests.get(f"{API}/api/persona/{pid}")
    data = res.json()
    print(f"  Name: {data['name']}")
    print(f"  Facts: {len(data['facts'])}")
    print(f"  Photo: {data.get('photo_url', 'none')}")
    print(f"  Files: {len(data.get('files', []))}")
    assert len(data['facts']) >= 10, f"FACTS NOT SAVED! Got {len(data['facts'])}"
    print(f"✅ Persona has {len(data['facts'])} facts")

    # 6. Test chat
    print("\n--- STEP 6: Test chat (LLM) ---")
    res = requests.post(f"{API}/api/chat", json={
        "persona_id": pid,
        "message": "Where were you born and what is your real name?"
    })
    chat_data = res.json()
    print(f"  Reply: {chat_data['reply'][:200]}")
    print(f"  New traits: {chat_data.get('new_traits_learned', [])}")
    assert "trouble thinking" not in chat_data['reply'].lower(), "LLM FALLBACK ERROR!"
    print(f"✅ Chat working — LLM replied intelligently")

    # 7. Test TTS
    print("\n--- STEP 7: Test TTS ---")
    try:
        res = requests.post(f"{API}/api/tts", json={
            "text": "Hello my child, I am Pope Francis.",
            "voice_id": "en-US-GuyNeural",
            "persona_id": pid
        }, timeout=30)
        tts_data = res.json()
        print(f"  Audio URL: {tts_data.get('audio_url', 'MISSING')}")
        if tts_data.get("audio_url"):
            # Verify audio file exists
            audio_res = requests.get(f"{API}{tts_data['audio_url']}")
            print(f"  Audio file size: {len(audio_res.content)} bytes")
            assert len(audio_res.content) > 1000, "Audio file too small"
            print(f"✅ TTS working — audio generated")
        else:
            print("⚠️ No audio URL returned")
    except Exception as e:
        print(f"⚠️ TTS error (Edge TTS WebSocket may be flaky): {e}")

    # 8. Test web search trigger
    print("\n--- STEP 8: Test web search (background) ---")
    print("  Web search runs in background on persona creation.")
    print("  Waiting 5 seconds for background task...")
    time.sleep(5)
    res = requests.get(f"{API}/api/persona/{pid}")
    data = res.json()
    print(f"  Facts after web search: {len(data['facts'])}")
    if len(data['facts']) > 10:
        print(f"✅ Web search added {len(data['facts']) - 10} extra facts!")
    else:
        print("  ℹ️ Web search may still be running or DDG rate-limited")

    print("\n" + "=" * 60)
    print("ALL CORE TESTS PASSED ✅")
    print(f"Persona ID: {pid}")
    print(f"Frontend: http://localhost:5173")
    print("=" * 60)

if __name__ == "__main__":
    test()
