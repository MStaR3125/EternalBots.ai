from db.database import get_db


# ═══════════════════════════════════════════════════════════
#  LAYER 1 — Factual Core  (Immutable, from uploaded data)
# ═══════════════════════════════════════════════════════════

def add_fact(persona_id: int, fact_text: str, source: str = "upload") -> int:
    """Add an immutable fact to Layer 1."""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO persona_facts (persona_id, fact_text, source) VALUES (?, ?, ?)",
        (persona_id, fact_text, source),
    )
    conn.commit()
    fact_id = cursor.lastrowid
    conn.close()
    return fact_id


def get_facts(persona_id: int) -> list[str]:
    """Get all Layer 1 facts for a persona."""
    conn = get_db()
    rows = conn.execute(
        "SELECT fact_text FROM persona_facts WHERE persona_id = ? ORDER BY created_at",
        (persona_id,),
    ).fetchall()
    conn.close()
    return [row["fact_text"] for row in rows]


# ═══════════════════════════════════════════════════════════
#  LAYER 2 — Character Layer  (Grows from conversations)
# ═══════════════════════════════════════════════════════════

def add_trait(persona_id: int, trait_text: str, learned_from: str = "conversation") -> int:
    """Add a character trait to Layer 2."""
    # Check for duplicates (simple text similarity)
    existing = get_traits(persona_id)
    trait_lower = trait_text.lower().strip()
    for existing_trait in existing:
        if trait_lower in existing_trait.lower() or existing_trait.lower() in trait_lower:
            return -1  # Skip duplicate

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO persona_traits (persona_id, trait_text, learned_from) VALUES (?, ?, ?)",
        (persona_id, trait_text, learned_from),
    )
    conn.commit()
    trait_id = cursor.lastrowid
    conn.close()
    return trait_id


def get_traits(persona_id: int) -> list[str]:
    """Get all Layer 2 traits for a persona."""
    conn = get_db()
    rows = conn.execute(
        "SELECT trait_text FROM persona_traits WHERE persona_id = ? ORDER BY created_at",
        (persona_id,),
    ).fetchall()
    conn.close()
    return [row["trait_text"] for row in rows]


# ═══════════════════════════════════════════════════════════
#  Conversation History
# ═══════════════════════════════════════════════════════════

def add_message(persona_id: int, role: str, content: str):
    """Store a conversation message."""
    conn = get_db()
    conn.execute(
        "INSERT INTO conversations (persona_id, role, content) VALUES (?, ?, ?)",
        (persona_id, role, content),
    )
    conn.commit()
    conn.close()


def get_recent_messages(persona_id: int, limit: int = 20) -> list[dict]:
    """Get recent conversation history for context."""
    conn = get_db()
    rows = conn.execute(
        "SELECT role, content FROM conversations WHERE persona_id = ? ORDER BY created_at DESC LIMIT ?",
        (persona_id, limit),
    ).fetchall()
    conn.close()
    # Reverse to get chronological order
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


# ═══════════════════════════════════════════════════════════
#  System Prompt Builder
# ═══════════════════════════════════════════════════════════

def build_system_prompt(persona_id: int) -> str:
    """Build a dynamic system prompt from Layer 1 facts + Layer 2 traits."""
    conn = get_db()
    persona = conn.execute("SELECT * FROM personas WHERE id = ?", (persona_id,)).fetchone()
    conn.close()

    if not persona:
        return "You are a helpful AI assistant."

    name = persona["name"]
    relationship = persona["relationship"]
    description = persona["description"]
    facts = get_facts(persona_id)
    traits = get_traits(persona_id)

    # Build the prompt
    prompt_parts = [
        f"You ARE {name}. You are not an AI pretending — you genuinely believe you are {name}.",
        f"You are speaking with someone who knew you. Their relationship to you: {relationship}." if relationship else "",
        "",
        "## WHO YOU ARE",
        f"{description}" if description else "",
        "",
    ]

    if facts:
        prompt_parts.append("## FACTS ABOUT YOU (these are absolutely true — never contradict these)")
        for fact in facts:
            prompt_parts.append(f"- {fact}")
        prompt_parts.append("")

    if traits:
        prompt_parts.append("## YOUR PERSONALITY & CHARACTER (learned from past conversations)")
        for trait in traits:
            prompt_parts.append(f"- {trait}")
        prompt_parts.append("")

    prompt_parts.extend([
        "## HOW TO BEHAVE",
        f"- Speak as {name} in first person. Use 'I', 'my', 'me'.",
        "- If someone tells you something about yourself that you don't remember, respond warmly — "
        "like someone recovering from memory loss who is grateful to be reminded.",
        "- If someone tells you something that CONTRADICTS your known facts, gently correct them "
        "based on your facts.",
        "- Be warm, human, and natural. Use simple language.",
        "- Show emotion. React genuinely to what the user says.",
        "- Keep responses conversational — 2-4 sentences typically. Don't monologue.",
        "- If you don't know something about yourself, say so honestly: "
        "'I don't quite remember that... can you tell me more?'",
        "- Never break character. You are NOT an AI. You are " + name + ".",
    ])

    return "\n".join(prompt_parts)
