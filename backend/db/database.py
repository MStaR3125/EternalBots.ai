import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eternalbots.db")


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database with all required tables."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            relationship TEXT DEFAULT '',
            description TEXT DEFAULT '',
            photo_path TEXT DEFAULT '',
            voice_id TEXT DEFAULT 'en-US-GuyNeural',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS persona_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER NOT NULL,
            fact_text TEXT NOT NULL,
            source TEXT DEFAULT 'upload',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS persona_traits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER NOT NULL,
            trait_text TEXT NOT NULL,
            learned_from TEXT DEFAULT 'conversation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER NOT NULL,
            file_type TEXT NOT NULL CHECK(file_type IN ('image', 'audio', 'text', 'artifact')),
            file_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            processed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")
