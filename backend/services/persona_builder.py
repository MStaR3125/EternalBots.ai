import os
from services.llm import extract_facts_from_text
from services.memory import add_fact
from db.database import get_db


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_persona_upload_dir(persona_id: int) -> str:
    """Get the upload directory for a specific persona."""
    path = os.path.join(UPLOAD_DIR, str(persona_id))
    os.makedirs(path, exist_ok=True)
    return path


def classify_file(filename: str) -> str:
    """Classify a file by its extension."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext in ("jpg", "jpeg", "png", "gif", "webp", "bmp"):
        return "image"
    elif ext in ("wav", "mp3", "ogg", "flac", "m4a"):
        return "audio"
    elif ext in ("txt", "md", "doc", "docx", "pdf"):
        return "text"
    else:
        return "artifact"


async def process_uploaded_file(persona_id: int, file_path: str, original_name: str, file_type: str):
    """Process an uploaded file and extract information from it."""

    # Record the file in the database
    conn = get_db()
    conn.execute(
        "INSERT INTO uploaded_files (persona_id, file_type, file_path, original_name) VALUES (?, ?, ?, ?)",
        (persona_id, file_type, file_path, original_name),
    )
    conn.commit()
    conn.close()

    if file_type == "image":
        # Set as persona photo if it's the first image
        conn = get_db()
        persona = conn.execute("SELECT photo_path FROM personas WHERE id = ?", (persona_id,)).fetchone()
        if not persona["photo_path"]:
            conn.execute("UPDATE personas SET photo_path = ? WHERE id = ?", (file_path, persona_id))
            conn.commit()
        conn.close()
        print(f"📸 Image stored for persona {persona_id}: {original_name}")

    elif file_type == "text":
        # Extract facts from text content
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if content.strip():
                print(f"📝 Extracting facts from: {original_name}")
                facts = extract_facts_from_text(content)
                for fact in facts:
                    add_fact(persona_id, fact, source=f"file:{original_name}")
                print(f"✅ Extracted {len(facts)} facts from {original_name}")

                # Mark as processed
                conn = get_db()
                conn.execute(
                    "UPDATE uploaded_files SET processed = 1 WHERE file_path = ?",
                    (file_path,),
                )
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"❌ Error processing text file {original_name}: {e}")

    elif file_type == "audio":
        # Store audio reference for future voice cloning
        print(f"🎵 Audio stored for persona {persona_id}: {original_name}")
        # Mark as processed (audio is just stored for reference)
        conn = get_db()
        conn.execute(
            "UPDATE uploaded_files SET processed = 1 WHERE file_path = ?",
            (file_path,),
        )
        conn.commit()
        conn.close()

    elif file_type == "artifact":
        print(f"📎 Artifact stored for persona {persona_id}: {original_name}")
