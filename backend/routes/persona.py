from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from models.schemas import PersonaCreate, PersonaResponse
from db.database import get_db
from services.persona_builder import (
    get_persona_upload_dir,
    classify_file,
    process_uploaded_file,
)
from services.memory import get_facts, get_traits
from services.web_search import perform_web_search_for_facts
import os
import shutil

router = APIRouter(prefix="/api/persona", tags=["Persona"])


@router.post("", response_model=dict)
async def create_persona(persona: PersonaCreate, background_tasks: BackgroundTasks):
    """Create a new persona and immediately fetch facts from the web in the background."""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO personas (name, relationship, description, voice_id) VALUES (?, ?, ?, ?)",
        (persona.name, persona.relationship, persona.description, persona.voice_id),
    )
    conn.commit()
    persona_id = cursor.lastrowid
    conn.close()

    # Create upload directory
    get_persona_upload_dir(persona_id)

    print(f"✅ Created persona: {persona.name} (ID: {persona_id})")
    
    # Launch background search for facts
    background_tasks.add_task(perform_web_search_for_facts, persona_id)
    
    return {"id": persona_id, "name": persona.name}


@router.get("s", response_model=list)
async def list_personas():
    """List all personas."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM personas ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/{persona_id}")
async def get_persona(persona_id: int):
    """Get full persona details including facts and traits."""
    conn = get_db()
    persona = conn.execute("SELECT * FROM personas WHERE id = ?", (persona_id,)).fetchone()
    conn.close()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    facts = get_facts(persona_id)
    traits = get_traits(persona_id)

    # Get uploaded files
    conn = get_db()
    files = conn.execute(
        "SELECT * FROM uploaded_files WHERE persona_id = ? ORDER BY created_at DESC",
        (persona_id,),
    ).fetchall()
    conn.close()

    result = dict(persona)
    result["facts"] = facts
    result["traits"] = traits
    result["files"] = [dict(f) for f in files]

    # Fix photo_path to be a URL
    if result["photo_path"]:
        result["photo_url"] = f"/uploads/{persona_id}/{os.path.basename(result['photo_path'])}"
    else:
        result["photo_url"] = ""

    return result


@router.post("/{persona_id}/upload")
async def upload_file(persona_id: int, file: UploadFile = File(...)):
    """Upload a file for a persona (image, audio, text, artifact)."""
    # Verify persona exists
    conn = get_db()
    persona = conn.execute("SELECT id FROM personas WHERE id = ?", (persona_id,)).fetchone()
    conn.close()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Classify and save the file
    file_type = classify_file(file.filename)
    upload_dir = get_persona_upload_dir(persona_id)
    file_path = os.path.join(upload_dir, file.filename)

    # Save file using shutil
    with open(file_path, "wb") as buffer:
        import shutil
        shutil.copyfileobj(file.file, buffer)

    # Process the file (extract facts, set photo, etc.)
    await process_uploaded_file(persona_id, file_path, file.filename, file_type)

    return {
        "filename": file.filename,
        "file_type": file_type,
        "status": "uploaded and processing",
    }


@router.post("/{persona_id}/facts")
async def add_manual_fact(persona_id: int, fact_text: str = Form(...)):
    """Manually add a fact to Layer 1."""
    from services.memory import add_fact
    fact_id = add_fact(persona_id, fact_text, source="manual")
    return {"id": fact_id, "fact_text": fact_text}


@router.delete("/{persona_id}")
async def delete_persona(persona_id: int):
    """Delete a persona and all associated data."""
    conn = get_db()
    conn.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
    conn.commit()
    conn.close()

    # Remove uploaded files
    upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "uploads",
        str(persona_id),
    )
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)

    return {"status": "deleted"}
