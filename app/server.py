import gradio as gr
import asyncio
import time
import os
import sys

# Add current directory to path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt import stt
from chatbot import reply
from tts import speak
from avatar import animate

# Start STT after import
stt.start()

DESCRIPTION = """
🎤 **Live AI Demo** - Ask Pope Francis anything and receive his answer in his own voice with an animated avatar.  
*(Everything runs locally; no data leaves your laptop.)*

**Instructions:**
1. **Allow microphone access** when prompted by your browser
2. **Speak clearly** into your microphone
3. **Click "Process Audio"** to process your speech and get a response
4. **Wait for the response** - TTS generation may take a moment on first use
"""

def process_audio():
    """Process audio input and return response"""
    last_result = getattr(process_audio, 'last_result', "")
    
    current_result = stt.result.strip() if stt.result else ""
    
    if current_result and current_result != last_result and len(current_result) > 3:
        process_audio.last_result = current_result
        
        try:
            print(f"🎤 Question detected: {current_result}")
            
            # Generate response
            print("🤖 Generating Pope Francis response...")
            response = reply(current_result)
            print(f"💭 Response: {response}")
            
            # Generate speech
            print("🔊 Generating speech...")
            wav_path = speak(response)
            
            # Generate avatar animation
            print("🎬 Creating avatar animation...")
            video_path = animate(wav_path)
            
            # Ensure video file exists and is accessible
            if video_path and os.path.exists(video_path):
                print(f"✅ Avatar video created: {video_path}")
                # Format the conversation
                conversation = f"""**Your Question:** {current_result}

**Pope Francis responds:** {response}"""
                
                status_msg = f"✅ Response generated successfully! Video: {os.path.basename(video_path)}"
                
                return video_path, conversation, status_msg
            else:
                print("❌ Avatar video generation failed")
                conversation = f"""**Your Question:** {current_result}

**Pope Francis responds:** {response}

*Note: Avatar video could not be generated, but audio response was created.*"""
                
                status_msg = f"⚠️ Response generated (audio: {os.path.basename(wav_path)}) but video failed"
                
                return None, conversation, status_msg
            
        except Exception as e:
            error_msg = f"❌ Error processing request: {str(e)}"
            print(error_msg)
            return None, f"**Error:** {error_msg}", "❌ Processing failed"
    
    elif not current_result:
        return None, "🎤 **Listening...** Please speak into your microphone and then click Process Audio.", "🎤 Ready - Microphone listening..."
    
    else:
        return None, f"🔄 **Last detected:** {current_result}\n\n*Speak something new and click Process Audio*", "⏳ Waiting for new speech input..."

def clear_conversation():
    """Clear the conversation and reset"""
    process_audio.last_result = ""
    stt.result = ""
    return None, "🎤 **Conversation cleared!** Speak into your microphone and click Process Audio.", "🔄 Ready for new conversation"

def get_system_status():
    """Get current system status"""
    whisper_status = "✅ Ready" if hasattr(stt, 'model') and stt.model else "❌ Not loaded"
    mic_status = "🎤 Listening" if stt.running else "❌ Not active"
    
    current_input = stt.result if stt.result else "None detected"
    
    return f"""**System Status:**
- **Speech Recognition:** {whisper_status}
- **Microphone:** {mic_status}  
- **Current Input:** {current_input}
- **TTS Model:** Will load on first use
- **Avatar:** Enhanced placeholder ready"""

# Custom CSS for better styling
css = """
.gradio-container {
    max-width: 1200px !important;
}
.main-header {
    text-align: center;
    margin-bottom: 20px;
}
.status-box {
    background-color: #f0f0f0;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
"""

with gr.Blocks(title="EternalBots – Pope Francis", css=css) as demo:
    gr.HTML("""
    <div class="main-header">
        <h1>🕊️ EternalBots – Pope Francis AI 🕊️</h1>
    </div>
    """)
    
    gr.Markdown(DESCRIPTION)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎬 Avatar Response")
            video = gr.Video(label="Pope Francis Avatar", interactive=False, height=400)
            
            with gr.Row():
                process_btn = gr.Button("🎤 Process Audio", variant="primary", size="lg")
                clear_btn = gr.Button("🔄 Clear Conversation", variant="secondary")
                status_btn = gr.Button("📊 System Status", variant="secondary")
        
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Conversation")
            chat = gr.Markdown(value="🎤 **Ready!** Speak into your microphone and click 'Process Audio' to begin...", height=300)
            
            gr.Markdown("### 📊 Status")
            status = gr.Textbox(label="Current Status", value="🎤 Ready - Microphone listening...", interactive=False)
            
            gr.Markdown("### ℹ️ Tips")
            gr.Markdown("""
            - **Speak clearly** and wait a moment after speaking
            - **First TTS generation** may take 1-2 minutes to download models
            - **Use simple questions** for best results
            - **Check system status** if having issues
            """)
    
    # Event handlers
    process_btn.click(
        fn=process_audio,
        outputs=[video, chat, status]
    )
    
    clear_btn.click(
        fn=clear_conversation,
        outputs=[video, chat, status]
    )
    
    status_btn.click(
        fn=get_system_status,
        outputs=[chat]
    )

if __name__ == "__main__":
    print("🚀 Starting EternalBots Pope Francis server...")
    print("🌐 Access the interface at: http://127.0.0.1:7861")
    demo.queue().launch(
        server_name="127.0.0.1", 
        server_port=7861,  # Changed to avoid port conflict
        share=False,
        show_error=True
    )
