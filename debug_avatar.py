#!/usr/bin/env python3
"""
Test script to debug avatar generation with Pope's face
"""

import sys
import os
sys.path.append('app')

def test_pope_image():
    """Test if we can load the Pope's image"""
    import cv2
    
    face_path = "data/pope_face.jpg"
    print(f"Checking for Pope's face image at: {face_path}")
    print(f"File exists: {os.path.exists(face_path)}")
    
    if os.path.exists(face_path):
        # Get file size
        file_size = os.path.getsize(face_path)
        print(f"File size: {file_size} bytes")
        
        # Try to load the image
        img = cv2.imread(face_path)
        if img is not None:
            print(f"Image loaded successfully!")
            print(f"Image dimensions: {img.shape}")
            return True
        else:
            print("❌ Failed to load image with cv2.imread")
            return False
    else:
        print("❌ Pope's face image not found!")
        return False

def test_avatar_creation():
    """Test avatar creation with Pope's face"""
    print("\n🎬 Testing avatar creation...")
    
    try:
        from avatar import animate
        
        # Test with existing image
        video_path = animate("dummy_audio.wav", "data/pope_face.jpg")
        print(f"✅ Avatar created: {video_path}")
        
        # Check if it's a real video file
        file_size = os.path.getsize(video_path)
        print(f"Video file size: {file_size} bytes")
        
        # Try to read the video
        import cv2
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video properties:")
            print(f"  - Frames: {frame_count}")
            print(f"  - FPS: {fps}")
            print(f"  - Resolution: {width}x{height}")
            
            # Read first frame
            ret, frame = cap.read()
            if ret:
                print(f"  - First frame loaded successfully!")
                # Check if it's not just black
                mean_brightness = frame.mean()
                print(f"  - Mean brightness: {mean_brightness}")
            cap.release()
            
        return True
        
    except Exception as e:
        print(f"❌ Avatar creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debugging Pope Francis Avatar Generation")
    print("=" * 50)
    
    # Test 1: Check Pope's image
    image_ok = test_pope_image()
    
    # Test 2: Test avatar creation
    avatar_ok = test_avatar_creation()
    
    print("\n" + "=" * 50)
    print("🎯 Debug Summary:")
    print(f"Pope's Image: {'✅ OK' if image_ok else '❌ FAIL'}")
    print(f"Avatar Creation: {'✅ OK' if avatar_ok else '❌ FAIL'}")
    
    if image_ok and avatar_ok:
        print("🎉 Avatar should be working with Pope's face!")
    else:
        print("⚠️ Issues detected that need fixing.")
