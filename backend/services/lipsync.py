import os
import requests
import time
from dotenv import load_dotenv
from db.database import get_db

load_dotenv()


def generate_did_video(audio_filepath: str, persona_id: int) -> str:
    """
    Generates a lip-sync video using the D-ID API.
    Takes the full local path to the generated audio and the persona's photo.
    Returns the URL of the generated video, or None if failed/disabled.
    """
    api_key = os.getenv("DID_API_KEY", "")
    if not api_key:
        return None
        
    conn = get_db()
    persona = conn.execute("SELECT photo_path FROM personas WHERE id = ?", (persona_id,)).fetchone()
    conn.close()
    
    if not persona or not persona["photo_path"]:
        print(f"⚠️ No photo found for persona {persona_id}. Skipping lip-sync.")
        return None
    
    full_image_path = persona["photo_path"]
    
    if not os.path.exists(full_image_path):
        print(f"⚠️ Photo file not found: {full_image_path}")
        return None

    if not os.path.exists(audio_filepath):
        print(f"⚠️ Audio file not found: {audio_filepath}")
        return None
    
    print("🔄 Requesting lip-sync video from D-ID...")
    
    headers = {
        "Authorization": f"Basic {api_key}",
        "Accept": "application/json"
    }

    try:
        # Step 1: Upload the image to D-ID
        print("  📸 Uploading image to D-ID...")
        with open(full_image_path, "rb") as img_file:
            img_res = requests.post(
                "https://api.d-id.com/images",
                headers=headers,
                files={"image": (os.path.basename(full_image_path), img_file, "image/jpeg")}
            )
            if img_res.status_code != 201:
                print(f"  ❌ Image upload failed: {img_res.status_code} {img_res.text[:200]}")
                return None
            source_url = img_res.json()["url"]
            print(f"  ✅ Image uploaded: {source_url[:60]}...")
            
        # Step 2: Upload the audio to D-ID
        print("  🔊 Uploading audio to D-ID...")
        with open(audio_filepath, "rb") as aud_file:
            aud_res = requests.post(
                "https://api.d-id.com/audios",
                headers=headers,
                files={"audio": (os.path.basename(audio_filepath), aud_file, "audio/mpeg")}
            )
            if aud_res.status_code != 201:
                print(f"  ❌ Audio upload failed: {aud_res.status_code} {aud_res.text[:200]}")
                return None
            audio_url = aud_res.json()["url"]
            print(f"  ✅ Audio uploaded: {audio_url[:60]}...")
            
        # Step 3: Create the Talk (lip-sync video)
        print("  🎬 Creating lip-sync talk...")
        talk_payload = {
            "source_url": source_url,
            "script": {
                "type": "audio",
                "audio_url": audio_url
            },
            "config": {
                "fluent": False,
                "pad_audio": 0.0
            }
        }
        
        talk_res = requests.post(
            "https://api.d-id.com/talks", 
            headers={**headers, "Content-Type": "application/json"},
            json=talk_payload
        )
        if talk_res.status_code not in [200, 201]:
            print(f"  ❌ Talk creation failed: {talk_res.status_code} {talk_res.text[:200]}")
            return None
            
        talk_id = talk_res.json()["id"]
        print(f"  ⏳ Waiting for D-ID video generation (Talk ID: {talk_id})...")
        
        # Step 4: Poll for completion (max 60 seconds)
        for i in range(30):
            status_res = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
            status_data = status_res.json()
            status = status_data.get("status", "unknown")
            
            if status == "done":
                video_url = status_data.get("result_url")
                print(f"  ✅ D-ID lip-sync video ready!")
                return video_url
            elif status in ["error", "rejected"]:
                print(f"  ❌ D-ID generation failed: {status_data.get('error', status_data)}")
                return None
            else:
                print(f"  ⏳ Status: {status} ({i+1}/30)...")
                
            time.sleep(2)
            
        print("  ❌ D-ID generation timed out after 60 seconds.")
        return None

    except Exception as e:
        print(f"❌ D-ID API error: {e}")
        return None
