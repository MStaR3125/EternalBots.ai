import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Testing TTS ===")
from tts import speak, detect_language
lang = detect_language("Hello Pope Francis")
print(f"Language: {lang}")
wav = speak("My dear friend, peace be with you.")
print(f"WAV: {wav}, size: {os.path.getsize(wav)} bytes")

print("\n=== Testing Avatar (SadTalker) ===")
from avatar import animate, _try_sadtalker
face = "data/pope_face.jpg"
print(f"Face exists: {os.path.exists(face)}")
result = _try_sadtalker(face, wav, "tmp/test_sadtalker.mp4")
print(f"SadTalker result: {result}")

if not result:
    print("\n=== Falling back to OpenCV ===")
    from avatar import _opencv_animate
    result = _opencv_animate(face, wav, "tmp/test_opencv.mp4")
    print(f"OpenCV result: {result}")
