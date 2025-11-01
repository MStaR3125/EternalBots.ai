# EternalBots Pope Francis - Setup Complete! 🕊️

## ✅ What's Been Set Up

Your EternalBots Pope Francis AI project is now configured and ready to run with Python 3.13!

### Environment Configuration
- **Virtual Environment**: `.venv` (Python 3.13)
- **Dependencies**: All core packages installed
- **Modified Requirements**: `requirements-py313.txt` created for Python 3.13 compatibility

### Important Notes

#### TTS Limitation
The TTS (Text-to-Speech) library doesn't officially support Python 3.13 yet, so the project will use:
- **Silent audio fallback** when TTS is unavailable
- The code is designed to gracefully handle this and continue working
- Voice cloning with XTTS-v2 will be skipped, but all other features work

#### Working Features
✅ Speech-to-Text (Whisper) - Microphone input working
✅ Chatbot (TinyLlama) - Pope Francis-style responses
✅ Avatar Animation (OpenCV) - Enhanced talking animations
✅ Gradio Web UI - Interactive interface
⚠️ Text-to-Speech - Falls back to silent audio (TTS not compatible with Python 3.13)

## 🚀 How to Run

### Option 1: Use the start script (Recommended)
```powershell
.\start.ps1
```

### Option 2: Use run.ps1
```powershell
.\run.ps1
```

### Option 3: Manual start
```powershell
.\.venv\Scripts\Activate.ps1
python app\server.py
```

### Option 4: Use the batch file (Windows)
```cmd
start.bat
```

## 🌐 Access the Application

Once started, open your browser to:
**http://127.0.0.1:7861**

The Gradio interface will allow you to:
1. Speak into your microphone
2. Click "Process Audio"
3. Receive Pope Francis-style responses
4. See an animated avatar (enhanced talking animation)

## 📁 Required Data Files

These files are already present in your `data/` folder:
- ✅ `data/pope_ref.wav` - Pope's voice reference (for TTS when available)
- ✅ `data/pope_face.jpg` - Pope's portrait for avatar

## 🔧 Troubleshooting

### If the server doesn't start:
1. Check that you're in the project directory
2. Make sure `.venv` is activated
3. Verify all imports work:
   ```powershell
   .\.venv\Scripts\python.exe -c "import torch; import whisper; import gradio; print('OK')"
   ```

### If microphone doesn't work:
- Allow microphone access in your browser when prompted
- Check Windows microphone permissions

### For better performance:
- The Whisper model downloads on first use (~70MB for tiny model)
- TinyLlama model downloads on first use (~2GB)
- First run may take a few minutes for model downloads

## 🎯 Next Steps to Enable Full TTS

To enable real voice cloning with Pope Francis' voice:
1. **Use Python 3.10 or 3.11** (TTS not compatible with 3.13 yet)
2. Create a new venv with Python 3.10/3.11:
   ```powershell
   py -3.11 -m venv .venv-py311
   .\.venv-py311\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## 📝 Key Files

- `app/server.py` - Main Gradio server
- `app/stt.py` - Speech-to-text with Whisper
- `app/chatbot.py` - TinyLlama Pope Francis responses
- `app/tts.py` - Text-to-speech (with fallback)
- `app/avatar.py` - Avatar animation
- `start.ps1` - Quick start script
- `start.bat` - Windows batch file to start
- `run.ps1` - Full setup and run script

## 🎉 You're All Set!

Run `.\start.ps1` and visit http://127.0.0.1:7861 to interact with Pope Francis AI!
