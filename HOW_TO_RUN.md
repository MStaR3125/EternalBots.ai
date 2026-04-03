# 🎉 EternalBots Pope Francis - Ready to Run!

## ✅ Setup Complete

Your project is now fully configured with:
- ✅ `.venv` virtual environment (Python 3.13)
- ✅ All dependencies installed
- ✅ Scripts created for easy launching
- ✅ Data files verified (pope_ref.wav, pope_face.jpg)

## 🚀 Quick Start

### Simple One-Command Start:
```powershell
.\start.ps1
```

Or double-click `start.bat` in Windows Explorer.

## 📥 First Run - Model Downloads

**Important**: On first run, the application will download AI models (~2GB total):
1. **Whisper tiny model** (~70MB) - for speech recognition
2. **TinyLlama 1.1B** (~2GB) - for Pope Francis responses

**You need an internet connection for the first run.** Subsequent runs will use cached models.

### Expected First-Run Process:
1. Whisper model loads (~5-10 seconds)
2. TinyLlama model downloads from Hugging Face (~5-10 minutes on good connection)
3. Server starts and displays URL
4. Open http://127.0.0.1:7861 in your browser

## 🎯 Using the Application

Once the server starts:

1. **Open your browser** to http://127.0.0.1:7861
2. **Allow microphone access** when prompted
3. **Speak into your microphone**
4. **Click "Process Audio"** button
5. **Wait for response** (voice + animated avatar)

## 📁 Project Structure

```
eternalbots-pope-francis/
├── .venv/                    # Virtual environment (Python 3.13)
├── app/
│   ├── server.py            # Main Gradio server
│   ├── stt.py               # Speech-to-Text (Whisper)
│   ├── chatbot.py           # Pope Francis AI responses (TinyLlama)
│   ├── tts.py               # Text-to-Speech (with fallback)
│   └── avatar.py            # Avatar animation
├── data/
│   ├── pope_ref.wav         # Pope's voice sample
│   └── pope_face.jpg        # Pope's portrait
├── tmp/                     # Temporary audio/video files
├── models/                  # Downloaded AI models (auto-created)
├── start.ps1                # Quick start script ⭐
├── start.bat                # Windows batch file ⭐
├── run.ps1                  # Full setup + run script
└── requirements-py313.txt   # Python 3.13 dependencies
```

## 🔧 Manual Start (Alternative Methods)

### Method 1: PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
python app\server.py
```

### Method 2: Command Prompt
```cmd
.venv\Scripts\activate.bat
python app\server.py
```

### Method 3: Direct Python
```powershell
.\.venv\Scripts\python.exe app\server.py
```

## ⚠️ Known Limitations (Python 3.13)

### TTS Voice Cloning Not Available
The `TTS` library doesn't support Python 3.13 yet, so:
- ❌ **Pope Francis voice cloning disabled**
- ✅ **Silent audio generated as fallback**
- ✅ **All other features work normally**

### To Enable Full Voice Cloning:
Use Python 3.10 or 3.11 instead:
```powershell
# If you have Python 3.11 installed:
py -3.11 -m venv .venv-py311
.\.venv-py311\Scripts\Activate.ps1
pip install -r requirements.txt
python app\server.py
```

## 🌐 Features

### ✅ Working Features:
- 🎤 **Live Speech Recognition** (Whisper)
- 🤖 **AI Chatbot** (Pope Francis personality via TinyLlama)
- 🎬 **Animated Avatar** (Enhanced OpenCV animations)
- 🖥️ **Web Interface** (Gradio UI)
- 📊 **System Status** monitoring

### ⚠️ Limited Features:
- 🔊 **Voice Synthesis** - Silent audio fallback (TTS incompatible with Python 3.13)

## 🐛 Troubleshooting

### Server won't start?
1. Make sure you're in the project directory
2. Check `.venv` is activated (you should see `(.venv)` in your prompt)
3. Verify internet connection for first-run downloads
4. Check for errors in the terminal output

### Test imports:
```powershell
.\.venv\Scripts\python.exe -c "import torch; import whisper; import gradio; import transformers; print('✅ All imports OK')"
```

### Models not downloading?
- Check your internet connection
- Try using a VPN if Hugging Face is blocked
- Models are downloaded from: https://huggingface.co/

### Microphone not working?
- Allow browser microphone permissions
- Check Windows Privacy Settings > Microphone
- Try Chrome/Edge (better WebRTC support)

### Port 7861 already in use?
Edit `app/server.py` line 187 and change `server_port=7861` to another port.

## 📊 Performance Tips

### First Run (One-time):
- Model downloads: ~5-10 minutes
- First model load: ~30-60 seconds
- Total setup time: ~10-15 minutes

### Subsequent Runs:
- Model loading: ~10-20 seconds
- Ready to use in under 30 seconds

### For GPU Acceleration:
If you have an NVIDIA GPU with CUDA:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
Then models will run much faster!

## 🎓 How It Works

1. **You speak** → Microphone captures audio
2. **Whisper** → Transcribes speech to text
3. **TinyLlama** → Generates Pope Francis-style response
4. **TTS** → Converts text to speech (or silent fallback)
5. **Avatar** → Creates animated video with talking motion
6. **Gradio** → Displays everything in web interface

## 📝 Next Steps

### To Run Now:
```powershell
.\start.ps1
```
Then open: **http://127.0.0.1:7861**

### To Stop:
Press `Ctrl+C` in the terminal

### To Restart:
Just run `.\start.ps1` again!

## 🆘 Need Help?

Check these files:
- `SETUP_COMPLETE.md` - This guide
- `README.md` - Original project documentation
- `app/server.py` - Main server code
- Terminal output - Look for error messages

---

## 🎉 You're Ready!

Everything is set up and ready to go. Just run:

```powershell
.\start.ps1
```

Then visit **http://127.0.0.1:7861** and start talking to Pope Francis! 🕊️

**Note**: First run will take 10-15 minutes to download models. Be patient! ⏳
