"""
server.py – EternalBots Pope Francis AI  (Upgraded)
Gradio web interface with:
  • Voice input (Whisper base, auto language detection)
  • Text input (Hinglish / Hindi / English)
  • XTTS-v2 voice cloning on GPU
  • SadTalker / D-ID / OpenCV lip-sync
"""

import os
import sys

# Force UTF-8 output so emoji/Unicode prints work on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import gradio as gr

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt import stt
from chatbot import reply, reset_history
from tts import speak
from avatar import animate

stt.start()

# ---------------------------------------------------------------------------
# Processing helpers
# ---------------------------------------------------------------------------
def _process(user_text: str, history: list):
    """Shared pipeline: LLM → TTS → avatar. Returns (video, updated_history, status)."""
    if not user_text or not user_text.strip():
        return None, history, "⚠️ No input received."

    user_text = user_text.strip()
    print(f"🎤 Input: {user_text}")

    try:
        response = reply(user_text)
        print(f"🤖 Response: {response[:80]}…")

        wav = speak(response)
        video = animate(wav)

        history = history + [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": response},
        ]

        if video and os.path.exists(video):
            status = f"✅ Done  |  video: {os.path.basename(video)}"
        else:
            status = "⚠️ Audio generated but video failed"
            video = None

        return video, history, status

    except Exception as e:
        status = f"❌ Error: {e}"
        print(status)
        return None, history, status


def process_voice(history: list):
    """Called by the 'Process Voice' button."""
    text = stt.result.strip() if stt.result else ""
    if not text or len(text) < 3:
        return None, history, "🎤 No speech detected yet. Speak into the mic first."
    # Clear so same utterance isn't replayed
    last = getattr(process_voice, "_last", "")
    if text == last:
        return None, history, "🔄 Same utterance already processed. Say something new."
    process_voice._last = text
    return _process(text, history)


def process_text(text_input: str, history: list):
    """Called by the 'Send' button or Enter key in text box."""
    return _process(text_input, history), "", history  # (outputs for 3 components)


def _process_text_split(text_input: str, history: list):
    """Splits return values for separate Gradio outputs."""
    video, hist, status = _process(text_input, history)
    return video, hist, status, ""  # blank clears the textbox


def clear_all(history: list):
    reset_history()
    stt.result = ""
    process_voice._last = ""
    return None, [], "🔄 Cleared. Ready for new conversation."


def get_status():
    whisper_ok = hasattr(stt, "model") and stt.model is not None
    mic_active = stt.running
    current = stt.result or "(nothing yet)"
    return (
        f"**Speech Recognition:** {'✅ Whisper base' if whisper_ok else '❌ Not loaded'}\n"
        f"**Microphone:** {'🎤 Active' if mic_active else '❌ Inactive'}\n"
        f"**Last heard:** {current}"
    )


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
css = """
.gradio-container { max-width: 1200px !important; }
.chat-panel { min-height: 380px; }
footer { display: none !important; }
"""

DESCRIPTION = """
### 🕊️ EternalBots – Pope Francis AI

Speak or type in **English, Hindi, or Hinglish**.
The avatar responds with a **cloned voice** and **lip-synced video**.

*Everything runs locally — no data leaves your machine.*
"""

with gr.Blocks(title="EternalBots – Pope Francis") as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        # ---- Left column: avatar video ----
        with gr.Column(scale=1):
            gr.Markdown("### 🎬 Avatar")
            video_out = gr.Video(
                label="Pope Francis", interactive=False, height=420, autoplay=True
            )

            with gr.Row():
                voice_btn = gr.Button("🎤 Process Voice", variant="primary")
                clear_btn = gr.Button("🗑 Clear", variant="secondary")
                status_btn = gr.Button("📊 Status", variant="secondary")

            status_box = gr.Textbox(
                label="Status",
                value="🎤 Ready — speak or type below…",
                interactive=False,
                lines=1,
            )

        # ---- Right column: chat ----
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Conversation")
            chatbot = gr.Chatbot(
                label="",
                height=360,
                elem_classes=["chat-panel"],
            )

            with gr.Row():
                text_in = gr.Textbox(
                    placeholder="Type in English, Hindi, or Hinglish…",
                    show_label=False,
                    scale=4,
                    lines=1,
                )
                send_btn = gr.Button("Send ➤", variant="primary", scale=1)

            gr.Markdown(
                "💡 **Tips:** Speak clearly → click *Process Voice*, or just type and press **Send**. "
                "Hinglish works perfectly — *aap kuch bhi pooch sakte ho!*"
            )

    # ---- Event wiring ----
    send_btn.click(
        fn=_process_text_split,
        inputs=[text_in, chatbot],
        outputs=[video_out, chatbot, status_box, text_in],
    )
    text_in.submit(
        fn=_process_text_split,
        inputs=[text_in, chatbot],
        outputs=[video_out, chatbot, status_box, text_in],
    )
    voice_btn.click(
        fn=process_voice,
        inputs=[chatbot],
        outputs=[video_out, chatbot, status_box],
    )
    clear_btn.click(
        fn=clear_all,
        inputs=[chatbot],
        outputs=[video_out, chatbot, status_box],
    )
    status_btn.click(
        fn=get_status,
        outputs=[status_box],
    )


if __name__ == "__main__":
    print("🚀 Starting EternalBots Pope Francis (Upgraded)…")
    print("🌐  http://127.0.0.1:7861")
    demo.queue().launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        css=css,
    )
