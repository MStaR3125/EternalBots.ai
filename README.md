# EternalBots.ai - Pope Francis Interactive AI Avatar

`Version_1.5` is a multimedia conversational AI prototype that simulates a spoken interaction with Pope Francis through a web interface. The project accepts microphone or typed input, generates a response in a Pope Francis-inspired persona, turns that response into speech, and then renders a lip-synced avatar video.

This branch is not just a lightweight demo. It includes the core application code, the `SadTalker` integration, bundled media assets, generated `tmp/` outputs, local model folders, and large binary assets tracked through Git LFS.

## What The Project Does

The end-to-end flow is:

1. The user speaks into the microphone or types a message.
2. Speech is transcribed with Whisper.
3. A Pope Francis-style response is generated with a Groq-hosted LLM.
4. The response is synthesized into audio using voice cloning or fallback TTS.
5. A talking avatar video is generated from `data/pope_face.jpg` plus the generated audio.
6. The final video is shown in a Gradio web UI along with the chat history.

The app is designed to support English, Hindi, and Hinglish interactions.

## Current Architecture

### 1. Web Interface

`app/server.py` provides the Gradio application. It exposes:

- a voice input flow using continuously captured microphone audio
- a text input flow for direct prompts
- a chat history panel
- a generated video output panel
- a status area for model and microphone state

The server runs locally by default at `http://127.0.0.1:7861`.

### 2. Speech Recognition

`app/stt.py` is responsible for microphone capture and transcription.

- It uses `sounddevice` to read from the system microphone.
- It loads the Whisper `base` model.
- It processes audio in short chunks and auto-detects language.
- It is tuned for English, Hindi, and Hinglish usage.

Important note: despite some older docs mentioning `faster-whisper`, the active branch code currently imports `whisper` from `openai-whisper`.

### 3. Conversational Brain

`app/chatbot.py` handles the LLM response generation.

- It uses the Groq API if `GROQ_API_KEY` is present.
- The configured model is `llama-3.3-70b-versatile`.
- It applies a system prompt that keeps the assistant in a Pope Francis-inspired pastoral persona.
- It attempts to mirror the user's language style:
  - English in, English out
  - Hindi in, Hindi out
  - Hinglish in, Hinglish out

If no Groq key is configured, the app falls back to a small set of hard-coded rule-based responses.

### 4. Text To Speech

`app/tts.py` turns the generated reply into audio.

It follows a three-tier fallback strategy:

1. XTTS-v2 voice cloning
   - Uses `data/pope_ref.wav` as the speaker reference
   - Can synthesize English and Hindi/Hinglish responses
   - Prefers GPU when available
2. `edge-tts` fallback
   - Uses standard neural voices
   - Works without local cloning weights
3. Silent placeholder audio
   - Used if the other methods fail

Language detection is done automatically from the text content before synthesis.

### 5. Avatar Generation

`app/avatar.py` creates the final talking video.

It also uses a three-tier fallback strategy:

1. SadTalker
   - Primary local lip-sync path
   - Uses `data/pope_face.jpg` and generated audio
   - Requires the `SadTalker/` code and model assets
2. D-ID API
   - Cloud backup if configured with `DID_API_KEY`
3. OpenCV fallback animation
   - Always-available local fallback
   - Generates a simpler animated video if the neural paths fail

This makes the project resilient: even if the full neural avatar stack is unavailable, the pipeline can still produce a result.

## What Is Included In This Branch

`Version_1.5` currently contains:

- the main app code under `app/`
- the `SadTalker/` repository contents and related checkpoints/assets
- `Wav2Lip/` source files
- `data/pope_face.jpg`
- `data/pope_ref.wav`
- `tmp/` generated outputs
- `models/` folders
- setup and helper scripts for Windows and PowerShell
- multiple markdown guides from development and setup work

Large media and model files are stored using Git LFS in this branch.

## Environment Variables

The project expects a `.env` file in the repository root. A safe template is provided in `.env.example`.

Key settings:

- `GROQ_API_KEY`
  Required for live LLM responses through Groq.
- `DID_API_KEY`
  Optional. Enables the D-ID cloud lip-sync fallback.
- `USE_VOICE_CLONING`
  Enables/disables XTTS voice cloning.
- `USE_SADTALKER`
  Enables/disables the local SadTalker avatar path.
- `USE_DID_LIPSYNC`
  Enables/disables D-ID usage.
- `TTS_ENGLISH_VOICE`
  Fallback voice for English via `edge-tts`.
- `TTS_HINDI_VOICE`
  Fallback voice for Hindi via `edge-tts`.

## Data Files

The project relies on two identity-specific files in `data/`:

- `data/pope_face.jpg`
  The portrait image used for avatar generation.
- `data/pope_ref.wav`
  The speaker reference clip used for voice cloning.

These are central to the current Pope Francis-specific version of the project.

## Setup

### Recommended Steps

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements-py313.txt
python app\server.py
```

Then open:

```text
http://127.0.0.1:7861
```

### Alternative Launch Scripts

Depending on your environment, you can also use:

- `start.ps1`
- `start.bat`
- `run.ps1`
- `run_upgraded.ps1`

## Dependency Notes

There is some historical drift in the docs and requirements files, so the most accurate source of truth is the code itself.

At the moment:

- `app/stt.py` uses `openai-whisper`
- `app/chatbot.py` uses Groq, not a local TinyLlama runtime
- `app/tts.py` expects XTTS-v2 if available, with fallbacks
- `app/avatar.py` expects SadTalker assets for the highest-quality local lip-sync path

`requirements-py313.txt` is the safer starting point for Python 3.13 environments.

## Runtime Characteristics

Depending on configuration, the app can operate in different modes:

- Full mode
  - Whisper transcription
  - Groq LLM responses
  - XTTS voice cloning
  - SadTalker lip-sync video
- Hybrid fallback mode
  - Whisper transcription
  - Groq or fallback responses
  - `edge-tts`
  - OpenCV or D-ID avatar generation
- Degraded local mode
  - Whisper if available
  - fallback text responses
  - silent audio
  - OpenCV animation

This layered design is one of the main strengths of the project: it keeps the demo usable even when some heavyweight components are missing or misconfigured.

## Intended Purpose

This project appears to be built as an educational, memorial, or demonstrative AI avatar system rather than as a production-ready deployment. The prompt and surrounding docs frame it as a simulation of Pope Francis for conversational interaction, multilingual dialogue, and voice/avatar experimentation.

In practical terms, it is a prototype that combines:

- speech recognition
- persona-based LLM interaction
- multilingual text-to-speech
- lip-sync avatar rendering
- a browser-based interface

## Known Caveats

- The branch contains large assets and generated files, so clones can be heavy.
- Git LFS is required for the large tracked media/model files.
- Some documentation files describe earlier project states and may not match the code exactly.
- The branch mixes source code, runtime artifacts, setup notes, and heavyweight model/media content in one place.
- The persona is implemented through prompt engineering rather than a fine-tuned local model.

## Short Summary

EternalBots.ai `Version_1.5` is a local-first AI avatar prototype for spoken and typed conversations with a simulated Pope Francis persona. It combines Whisper transcription, Groq-based response generation, XTTS or fallback speech synthesis, and SadTalker/D-ID/OpenCV avatar rendering inside a Gradio web app.
