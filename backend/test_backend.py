import requests
import time

API_URL = "http://localhost:8000"

def test_api():
    print("1. Testing TTS endpoint...")
    try:
        res = requests.post(f"{API_URL}/api/tts", json={
            "text": "Hello, world! This is a test.",
            "voice_id": "en-US-GuyNeural"
        })
        print(f"TTS response: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"TTS Error: {e}")

    print("\n2. Testing Chat endpoint (LLM)...")
    try:
        # Create a temp persona
        res = requests.post(f"{API_URL}/api/persona", json={
            "name": "Test Bot"
        })
        persona_id = res.json()["id"]
        
        # Test chat
        res = requests.post(f"{API_URL}/api/chat", json={
            "persona_id": persona_id,
            "message": "Hello, who are you?"
        })
        print(f"Chat response: {res.status_code} - {res.text}")
        
    except Exception as e:
        print(f"Chat Error: {e}")

if __name__ == "__main__":
    test_api()
