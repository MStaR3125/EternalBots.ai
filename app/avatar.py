import uuid, pathlib, shutil, os, sys
import cv2
import numpy as np

def animate(wav_path: str, face_path="data/pope_face.jpg") -> str:
    """Create a lip-synced video using SadTalker or fallback to enhanced static animation."""
    vid_dir = "tmp"
    pathlib.Path(vid_dir).mkdir(exist_ok=True)
    out = f"{vid_dir}/{uuid.uuid4().hex}.mp4"
    
    try:
        # Use absolute paths
        if not os.path.isabs(face_path):
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            face_path = os.path.join(current_dir, face_path)
        
        if not os.path.isabs(wav_path):
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            wav_path = os.path.join(current_dir, wav_path)
            
        print(f"Creating lip-sync avatar:")
        print(f"  Face: {face_path}")
        print(f"  Audio: {wav_path}")
        
        # Try SadTalker first for real lip-sync
        sadtalker_result = try_sadtalker(face_path, wav_path, out)
        if sadtalker_result:
            return sadtalker_result
            
        print("SadTalker not available, using enhanced static animation...")
        
        # Fallback to enhanced static animation
        if not os.path.exists(face_path):
            print(f"❌ Pope's face image not found at {face_path}")
            create_placeholder_video(out)
            return out
            
        img = cv2.imread(face_path)
        if img is None:
            print(f"❌ Failed to load image from {face_path}")
            create_placeholder_video(out)
            return out
            
        print(f"✅ Creating enhanced Pope Francis avatar...")
        create_enhanced_talking_video(img, wav_path, out)
        return out
        
    except Exception as e:
        print(f"Error creating avatar animation: {e}")
        create_placeholder_video(out)
        return out

def try_sadtalker(face_path: str, audio_path: str, output_path: str) -> str:
    """Try to use SadTalker for real lip-sync"""
    try:
        # Add SadTalker to path
        sadtalker_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SadTalker")
        if os.path.exists(sadtalker_path):
            sys.path.insert(0, sadtalker_path)
            
            print("🎭 Attempting to use SadTalker for real lip-sync...")
            
            # Import SadTalker modules
            from inference import main as sadtalker_main
            
            # Prepare arguments for SadTalker
            class Args:
                def __init__(self):
                    self.source_image = face_path
                    self.driven_audio = audio_path
                    self.result_dir = os.path.dirname(output_path)
                    self.still = True
                    self.preprocess = 'crop'
                    self.enhancer = None
                    self.background_enhancer = None
                    self.cpu = True
                    self.face3dvis = False
                    self.animate_from_audio = True
                    
            args = Args()
            
            # Run SadTalker
            result_path = sadtalker_main(args)
            
            if result_path and os.path.exists(result_path):
                # Move result to our expected location
                shutil.move(result_path, output_path)
                print(f"✅ SadTalker lip-sync avatar created: {output_path}")
                return output_path
                
        return None
        
    except Exception as e:
        print(f"SadTalker failed: {e}")
        return None

def create_enhanced_talking_video(img, audio_path: str, output_path: str):
    """Create enhanced talking animation that syncs with audio"""
    try:
        import soundfile as sf
        # Load audio to get duration
        audio_data, sample_rate = sf.read(audio_path)
        duration = len(audio_data) / sample_rate
    except:
        duration = 3  # Default duration
    
    print(f"Creating {duration:.1f}s talking animation...")
    
    # Resize image to standard size while maintaining aspect ratio
    height, width = 480, 640
    orig_height, orig_width = img.shape[:2]
    
    # Calculate scaling
    scale = min(width / orig_width, height / orig_height)
    new_width = int(orig_width * scale)
    new_height = int(orig_height * scale)
    
    img_resized = cv2.resize(img, (new_width, new_height))
    
    # Create background
    background = np.zeros((height, width, 3), dtype=np.uint8)
    background[:] = (15, 15, 25)  # Dark blue background
    
    # Center the image
    y_offset = (height - new_height) // 2
    x_offset = (width - new_width) // 2
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))
    
    frames = int(duration * 30)  # 30 fps
    
    for i in range(frames):
        frame = background.copy()
        
        # Create talking motion effects
        time_factor = i / 30.0  # Current time in seconds
        
        # Mouth movement simulation (faster for talking)
        mouth_movement = np.sin(time_factor * 8) * 0.01  # 8 Hz for talking
        
        # Head bob (subtle)
        head_bob = np.sin(time_factor * 1.5) * 0.005
        
        # Scale the image slightly based on talking
        scale_factor = 1.0 + mouth_movement + head_bob
        
        # Apply transformations
        if scale_factor > 0.95 and scale_factor < 1.05:
            scaled_width = int(new_width * scale_factor)
            scaled_height = int(new_height * scale_factor)
            
            scaled_img = cv2.resize(img_resized, (scaled_width, scaled_height))
            
            # Re-center
            new_y_offset = y_offset - (scaled_height - new_height) // 2
            new_x_offset = x_offset - (scaled_width - new_width) // 2
            
            # Ensure bounds
            if (new_y_offset >= 0 and new_x_offset >= 0 and 
                new_y_offset + scaled_height <= height and 
                new_x_offset + scaled_width <= width):
                frame[new_y_offset:new_y_offset+scaled_height, 
                      new_x_offset:new_x_offset+scaled_width] = scaled_img
            else:
                frame[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = img_resized
        else:
            frame[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = img_resized
        
        # Add speaking indicators
        pulse = (np.sin(time_factor * 6) + 1) / 2  # 6 Hz pulse for active speaking
        
        # Animated speaking indicator
        indicator_color = int(50 + 205 * pulse)
        cv2.circle(frame, (width - 50, 50), 15, (0, indicator_color, 0), -1)
        cv2.putText(frame, "LIVE", (width - 85, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Pope Francis branding
        alpha = 0.7 + 0.3 * np.sin(time_factor * 2)
        text_color = int(255 * alpha)
        cv2.putText(frame, "Pope Francis AI", (20, height - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (text_color, text_color, text_color), 2)
        cv2.putText(frame, "Speaking with AI Voice", (20, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (text_color//2, text_color//2, text_color//2), 1)
        
        # Audio waveform visualization (simulated)
        for j in range(0, width, 20):
            wave_height = int(20 * np.sin(time_factor * 10 + j * 0.1) * pulse)
            cv2.line(frame, (j, height - 10), (j, height - 10 - abs(wave_height)), (0, 100, 200), 2)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Enhanced talking Pope Francis avatar created with {frames} frames")

def create_placeholder_video(output_path: str):
    """Create a placeholder video when the Pope's image isn't available."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (640, 480))
    
    for i in range(90):  # 3 seconds at 30 fps
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (50, 50, 100)  # Dark blue background
        
        # Add text
        cv2.putText(frame, "EternalBots", (200, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(frame, "Pope Francis AI Avatar", (150, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        cv2.putText(frame, "Loading...", (280, 320), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2)
        
        out.write(frame)
    
    out.release()
    print("✅ Placeholder video created")
