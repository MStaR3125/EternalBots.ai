# EternalBots.ai v2

Build interactive AI personas from memories, documents, photos, and voice samples.

`Version_2` is a full-stack prototype for digitally preserving the conversational essence of a person. Instead of hardcoding a single character, this branch lets you create a persona, upload source material about them, extract factual memories, learn behavioral traits over time, and speak with them through a modern web interface.

## Why This Version Matters

This branch moves beyond the earlier single-avatar demo into a reusable memory engine.

You can:

- create a persona for a loved one or historical figure
- upload text, audio, and image material about them
- automatically extract factual memories from source files
- enrich the persona with web-searched facts
- chat with a persona that speaks in first person
- synthesize a voice response
- optionally generate a lip-synced video response
- let the system learn new character traits from conversation

The result is an experience that feels less like a chatbot and more like an evolving digital memory companion.

## Core Idea

EternalBots.ai v2 uses a two-layer memory model:

### Layer 1: Factual Core

This is the stable memory base.

- facts extracted from uploaded text
- facts discovered from background web search
- core biography and relationship context
- uploaded media references and artifacts

These are treated as the persona's ground truth and are used to keep responses consistent.

### Layer 2: Character Layer

This is the adaptive, learned layer.

- personality traits
- mannerisms
- preferences
- emotional tendencies
- conversational habits inferred over time

As users talk to the persona, the backend extracts new character traits and stores them for future responses.

## Product Flow

1. Create a persona with a name, relationship, description, and preferred voice.
2. Upload documents, photos, audio clips, or artifacts.
3. Extract facts from source files and enrich them with web search.
4. Build a dynamic prompt from facts, traits, and recent conversation history.
5. Generate a response through Groq.
6. Convert the reply to speech with Edge TTS, ElevenLabs, or OpenVoice-based cloning.
7. Optionally generate D-ID lip-sync video.
8. Continue chatting while the system learns more about who the persona is.

## Tech Stack

### Backend

- FastAPI
- SQLite
- Groq API
- Edge TTS
- optional ElevenLabs cloning
- optional OpenVoice cloning
- optional D-ID lip-sync

### Frontend

- Vite
- Vanilla JavaScript
- custom CSS
- Web Speech API for browser-side voice input

## Architecture

### Backend API

The backend lives in `backend/` and exposes three main API groups:

- `/api/persona`
  Create, list, inspect, upload data for, and delete personas.
- `/api/chat`
  Send user messages, generate persona replies, and learn new traits.
- `/api/tts`
  Generate speech and optionally trigger lip-sync video creation.

### Memory System

The memory engine lives mainly in:

- `backend/services/memory.py`
- `backend/services/persona_builder.py`
- `backend/services/llm.py`
- `backend/db/database.py`

This is where facts, traits, conversation history, and dynamic prompt assembly are handled.

### Frontend Experience

The frontend lives in `frontend/` and provides:

- a landing page for persona selection
- persona creation flow
- upload flow for files and manual facts
- real-time chat interface
- speech playback
- optional video playback
- visual indicators for speaking, learning, and system state

## Repository Structure

```text
Version_2
├── backend/
│   ├── db/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── uploads/
│   ├── audio_cache/
│   ├── .env
│   ├── .env.example
│   ├── eternalbots.db
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── main.js
│   ├── style.css
│   ├── package.json
│   └── vite.config.js
└── SampleData/
    ├── facts.txt
    ├── photo.jpg
    └── reference_audio.wav
```

## Current Capabilities

### Persona Creation

- create a persona profile
- assign relationship context
- choose a default voice

### Memory Ingestion

- upload image files
- upload text files
- upload reference audio
- manually add facts
- automatically classify uploaded files

### Fact Extraction

- extract structured facts from text uploads
- search the web for supporting biography context
- store facts in a persistent database

### Conversation

- maintain recent chat history
- generate first-person responses
- keep the persona grounded in known facts
- gently adapt when the user reveals more about the person

### Voice and Video

- Edge TTS for immediate speech generation
- ElevenLabs voice cloning if configured
- OpenVoice conversion if enabled
- D-ID lip-sync video generation if configured

## Running The Project

### Backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will typically run at:

```text
http://localhost:5173
```

## Environment Variables

The backend reads configuration from `backend/.env`.

Use `backend/.env.example` as the starting point.

Important keys:

- `GROQ_API_KEY`
  Required for LLM responses.
- `DID_API_KEY`
  Optional. Enables D-ID video lip-sync.
- `ELEVENLABS_API_KEY`
  Optional. Enables ElevenLabs voice cloning.
- `OPENVOICE_ENABLED`
  Optional. Enables OpenVoice post-processing.

## Included Sample Assets

This branch already includes:

- a seeded SQLite database
- cached/generated audio
- uploaded persona assets
- sample text, photo, and audio files under `SampleData/`

That makes the branch useful both as a runnable prototype and as a reference dataset for development.

## Best Use Cases

- memorial AI experiments
- interactive biography systems
- digital storytelling prototypes
- family memory preservation tools
- conversation-driven character reconstruction
- research demos for memory-grounded personas

## Important Caveats

- This is a prototype, not a hardened production platform.
- Some premium features depend on external APIs and paid services.
- The branch currently includes local runtime artifacts for convenience, which makes it heavier than a minimal source-only repo.
- Persona consistency depends on the quality of uploaded material and extracted facts.
- The system simulates a person through prompting, retrieval, and learned traits; it does not restore consciousness or exact identity.

## Vision

EternalBots.ai v2 is trying to answer a deeply human question:

How do we preserve not only what someone did, but how they spoke, remembered, reacted, and made us feel?

This branch is an early but ambitious step toward that vision: a memory-grounded AI persona system that can grow richer the more it is remembered.
