# EternalBots – Pope Francis Prototype (Minimal)

Local voice conversation loop:

Mic (Whisper small) -> TinyLlama reply -> XTTS-v2 cloned voice -> (placeholder avatar).

This repo was trimmed to only essential runnable pieces:

Components:
1. `app/stt.py` – streaming speech-to-text (faster-whisper).
2. `app/chatbot.py` – TinyLlama chat inference.
3. `app/tts.py` – XTTS-v2 voice cloning using `data/pope_ref.wav`.
4. `app/avatar.py` – placeholder mp4 generator (replace with SadTalker later).
5. `app/server.py` – Gradio UI orchestrating the loop.

Removed: embedded SadTalker source tree heavy assets, empty utils, unused dependency lines.

## Quick Start

```bash
python -m venv .venv
./.venv/Scripts/activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt
python app/server.py
```

Open http://127.0.0.1:7860 in a browser, allow microphone.

## GPU Option
Install CUDA torch wheel and set `device="cuda"` logic in `stt.py` / use `gpu=True` in `tts.py` if GPU available.

## Avatar Upgrade
Swap `avatar.py` stub with SadTalker call once models downloaded. Keep output mp4 path contract the same.

## Data
Place a 6–10 s clean Pope Francis voice clip at `data/pope_ref.wav` and a square 512px portrait at `data/pope_face.jpg` (portrait currently only referenced for future avatar step).

See root guide markdown for extended rationale and citations.
