import queue, threading, sounddevice as sd, numpy as np
import whisper
import time

class Streamer:
    def __init__(self, model_size="tiny"):  # Using tiny model for faster download
        self.model = None
        self.model_size = model_size
        self.q, self.result = queue.Queue(), ""
        self.running = False
        self._init_model()

    def _init_model(self):
        """Initialize model with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempting to load Whisper model (attempt {attempt + 1}/{max_retries})...")
                self.model = whisper.load_model(self.model_size)
                print("Whisper model loaded successfully!")
                break
            except Exception as e:
                print(f"Failed to load model on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print("Failed to load Whisper model after all attempts. Using dummy mode.")
                    self.model = None

    def _audio_cb(self, indata, frames, t, status):
        self.q.put(indata.copy())

    def listen(self):
        self.running = True
        with sd.InputStream(samplerate=16000, channels=1, callback=self._audio_cb):
            while self.running:
                if self.q.qsize()*1024/16000 > 1.5:          # 1.5 s chunk
                    if self.model is not None:
                        try:
                            chunk = np.concatenate([self.q.get() for _ in range(self.q.qsize())]).flatten()
                            result = self.model.transcribe(chunk)
                            self.result = result["text"].strip()
                        except Exception as e:
                            print(f"Transcription error: {e}")
                            # Clear the queue to prevent backup
                            while not self.q.empty():
                                self.q.get()
                    else:
                        # Dummy mode - simulate transcription
                        while not self.q.empty():
                            self.q.get()
                        self.result = "[Audio detected - Whisper model not available]"
                sd.sleep(50)

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

# Initialize with lazy loading
stt = Streamer()
