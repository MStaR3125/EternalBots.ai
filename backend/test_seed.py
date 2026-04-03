import requests
import os

API_URL = "http://localhost:8000"

DATA_DIR = r"c:\Users\micro\OneDrive\Desktop\ETERNAL_BOTS_AI\Model_1.0\eternalbots-pope-francis\data"
PHOTO_PATH = os.path.join(DATA_DIR, "pope_face.jpg")
AUDIO_PATH = os.path.join(DATA_DIR, "pope_ref.wav")

def seed_pope_francis():
    print("1. Creating Pope Francis persona...")
    res = requests.post(f"{API_URL}/api/persona", json={
        "name": "Pope Francis",
        "relationship": "Spiritual Leader",
        "description": "The head of the Catholic Church and sovereign of the Vatican City State.",
        "voice_id": "en-US-GuyNeural" # Or a suitable Edge TTS voice if cloning isn't on
    })
    
    if res.status_code != 200:
        print(f"Error creating persona: {res.text}")
        return
        
    persona_id = res.json()["id"]
    print(f"Created with ID: {persona_id}")
    
    print("2. Uploading photo...")
    if os.path.exists(PHOTO_PATH):
        with open(PHOTO_PATH, "rb") as f:
            res = requests.post(
                f"{API_URL}/api/persona/{persona_id}/upload", 
                files={"file": ("pope_face.jpg", f, "image/jpeg")}
            )
            print(f"Photo upload: {res.status_code}")
    
    print("3. Uploading reference audio...")
    if os.path.exists(AUDIO_PATH):
        with open(AUDIO_PATH, "rb") as f:
            res = requests.post(
                f"{API_URL}/api/persona/{persona_id}/upload", 
                files={"file": ("pope_ref.wav", f, "audio/wav")}
            )
            print(f"Audio upload: {res.status_code}")
            
    print("4. Uploading facts text...")
    facts_text = """
    Pope Francis was born Jorge Mario Bergoglio on 17 December 1936 in Buenos Aires, Argentina.
    He is the head of the Catholic Church, the bishop of Rome and sovereign of the Vatican City State.
    Francis is the first pope to be a member of the Society of Jesus (Jesuits).
    He is the first pope from the Americas and the first from the Southern Hemisphere.
    He chose the papal name Francis in honor of Saint Francis of Assisi.
    Throughout his public life, he has been noted for his humility, emphasis on God's mercy, 
    international visibility as pope, concern for the poor and commitment to interfaith dialogue.
    He is credited with having a less formal approach to the papacy.
    """
    
    # Save temp text file
    temp_txt = "temp_facts.txt"
    with open(temp_txt, "w", encoding="utf-8") as f:
        f.write(facts_text.strip())
        
    with open(temp_txt, "rb") as f:
        res = requests.post(
            f"{API_URL}/api/persona/{persona_id}/upload", 
            files={"file": ("facts.txt", f, "text/plain")}
        )
        print(f"Facts upload: {res.status_code}")
        
    os.remove(temp_txt)
    print("\n✅ Pope Francis seed complete! Check the UI.")

if __name__ == "__main__":
    seed_pope_francis()
