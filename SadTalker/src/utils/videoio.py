import shutil
import uuid
import subprocess

import os

import cv2

def load_video_to_cv2(input_path):
    video_stream = cv2.VideoCapture(input_path)
    fps = video_stream.get(cv2.CAP_PROP_FPS)
    full_frames = []
    while 1:
        still_reading, frame = video_stream.read()
        if not still_reading:
            video_stream.release()
            break
        full_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return full_frames

def _get_ffmpeg_bin():
    """Find ffmpeg: prefer imageio_ffmpeg bundled binary, then system PATH."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def save_video_with_watermark(video, audio, save_path, watermark=False):
    temp_file = str(uuid.uuid4())+'.mp4'
    ffmpeg_bin = _get_ffmpeg_bin()
    try:
        subprocess.run(
            [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
             "-i", video, "-i", audio, "-vcodec", "copy", temp_file],
            check=True, capture_output=True,
        )
    except Exception as e:
        print(f"[WARN] ffmpeg mux failed: {e}")
        # Fallback: just copy the video without audio
        shutil.copy2(video, temp_file)

    if watermark is False:
        shutil.move(temp_file, save_path)
    else:
        try:
            import webui
            from modules import paths
            watarmark_path = paths.script_path+"/extensions/SadTalker/docs/sadtalker_logo.png"
        except:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            watarmark_path = dir_path+"/../../docs/sadtalker_logo.png"

        try:
            subprocess.run(
                [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
                 "-i", temp_file, "-i", watarmark_path,
                 "-filter_complex", "[1]scale=100:-1[wm];[0][wm]overlay=(main_w-overlay_w)-10:10",
                 save_path],
                check=True, capture_output=True,
            )
        except Exception as e:
            print(f"[WARN] ffmpeg watermark failed: {e}")
            shutil.move(temp_file, save_path)
            return
        os.remove(temp_file)
