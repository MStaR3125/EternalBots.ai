#!/usr/bin/env python3
"""
Simple test script to check individual components
"""

import sys
import os
sys.path.append('app')

def test_avatar():
    """Test the improved avatar functionality"""
    print("🎬 Testing Avatar...")
    try:
        from avatar import animate
        video_path = animate("dummy_audio.wav")
        print(f"✅ Avatar test successful: {video_path}")
        return True
    except Exception as e:
        print(f"❌ Avatar test failed: {e}")
        return False

def test_chatbot():
    """Test the improved chatbot"""
    print("🤖 Testing Chatbot...")
    try:
        from chatbot import reply
        response = reply("Hello, Pope Francis!")
        print(f"✅ Chatbot test successful: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        return False

def test_tts():
    """Test the TTS functionality"""
    print("🔊 Testing TTS...")
    try:
        from tts import speak
        audio_path = speak("Hello, this is a test.")
        print(f"✅ TTS test successful: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_stt():
    """Test the STT functionality"""
    print("🎤 Testing STT...")
    try:
        from stt import stt
        print(f"✅ STT initialized: Model={stt.model is not None}")
        return True
    except Exception as e:
        print(f"❌ STT test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing EternalBots Components...")
    print("=" * 50)
    
    tests = [
        ("STT (Speech-to-Text)", test_stt),
        ("Chatbot", test_chatbot),
        ("Avatar", test_avatar),
        ("TTS (Text-to-Speech)", test_tts),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📝 {name}:")
        success = test_func()
        results.append((name, success))
        print("-" * 30)
    
    print("\n🎯 Test Summary:")
    print("=" * 50)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All components working! Ready to start server.")
    else:
        print("⚠️ Some components need attention.")
