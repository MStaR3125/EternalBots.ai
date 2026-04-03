"""
avatar.py – Lip-sync avatar generation for EternalBots Pope Francis

Tier 1 (primary): SadTalker on GPU (local, no API credits)
  - Real neural lip-sync from pope_face.jpg + generated audio
  - ~10-30 seconds on RTX 3050

Tier 2 (cloud backup): D-ID API
  - Upload image + audio → receive lip-synced video
  - ~10-15 seconds, uses free API credits

Tier 3 (offline): Improved OpenCV animation
  - Audio-amplitude-driven mouth animation
  - Always available, no external deps
"""

import uuid
import pathlib
import shutil
import os
import sys
import time
import subprocess
import requests
import cv2
import numpy as np
import soundfile as sf
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

USE_SADTALKER = os.getenv("USE_SADTALKER", "true").lower() == "true"
USE_DID = os.getenv("USE_DID_LIPSYNC", "true").lower() == "true"
DID_API_KEY = os.getenv("DID_API_KEY", "")

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cache D-ID uploaded image URL so we don't re-upload on every call
_did_image_url: str | None = None


def _get_ffmpeg() -> str | None:
    """Return path to ffmpeg binary, or None if unavailable."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    for candidate in ["ffmpeg", "/usr/bin/ffmpeg"]:
        try:
            subprocess.run([candidate, "-version"], capture_output=True, check=True)
            return candidate
        except Exception:
            pass
    return None


def _mux_audio(video_path: str, audio_path: str, output_path: str) -> bool:
    """Re-encode video to H.264 + mux in audio using ffmpeg. Returns True on success."""
    ffmpeg = _get_ffmpeg()
    if not ffmpeg:
        return False
    try:
        subprocess.run(
            [ffmpeg, "-y", "-i", video_path, "-i", audio_path,
             "-c:v", "libx264", "-preset", "fast", "-crf", "23",
             "-c:a", "aac", "-b:a", "128k", "-shortest", output_path],
            capture_output=True, check=True,
        )
        return True
    except Exception as e:
        print(f"[WARN] ffmpeg re-encode failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def animate(wav_path: str, face_path: str = "data/pope_face.jpg") -> str:
    """Create a lip-synced video. Returns path to mp4 in tmp/."""
    tmp_dir = os.path.join(_BASE, "tmp")
    pathlib.Path(tmp_dir).mkdir(exist_ok=True)
    out = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.mp4")

    # Resolve relative paths
    if not os.path.isabs(face_path):
        face_path = os.path.join(_BASE, face_path)
    if not os.path.isabs(wav_path):
        wav_path = os.path.join(_BASE, wav_path)

    print("[Avatar] Creating lip-sync avatar:")
    print(f"   Face : {face_path}")
    print(f"   Audio: {wav_path}")

    # --- Tier 1: SadTalker ---
    if USE_SADTALKER:
        result = _try_sadtalker(face_path, wav_path, out)
        if result:
            return result
        print("[Avatar] SadTalker unavailable, trying D-ID...")

    # --- Tier 2: D-ID ---
    if USE_DID and DID_API_KEY:
        result = _try_did(face_path, wav_path, out)
        if result:
            return result
        print("[Avatar] D-ID unavailable, using OpenCV fallback...")

    # --- Tier 3: OpenCV ---
    return _opencv_animate(face_path, wav_path, out)


# ---------------------------------------------------------------------------
# Tier 1 – SadTalker
# ---------------------------------------------------------------------------
def _try_sadtalker(face_path: str, audio_path: str, output_path: str) -> str | None:
    sadtalker_dir = os.path.join(_BASE, "SadTalker")
    checkpoints = os.path.join(sadtalker_dir, "checkpoints")

    if not os.path.exists(sadtalker_dir):
        print("[WARN] SadTalker directory not found")
        return None

    # Require at least the main safetensors model to be present
    main_model = os.path.join(checkpoints, "SadTalker_V0.0.2_256.safetensors")
    if not os.path.exists(main_model):
        print("[WARN] SadTalker checkpoints not downloaded yet")
        print("  Expected:", main_model)
        return None

    import torch
    _prev_dir = os.getcwd()
    try:
        # SadTalker must run from its own directory (uses relative paths internally)
        os.chdir(sadtalker_dir)
        if sadtalker_dir not in sys.path:
            sys.path.insert(0, sadtalker_dir)
        # Inject pytorch3d stub if pytorch3d is not installed
        stub_dir = os.path.join(sadtalker_dir, "pytorch3d_stub")
        try:
            import pytorch3d  # noqa: F401
        except ImportError:
            if stub_dir not in sys.path:
                sys.path.insert(0, stub_dir)
            print("[SadTalker] Using pytorch3d stub (renderer disabled, coefficients unaffected)")

        # Compat shim: torchvision.transforms.functional_tensor was removed in torchvision 0.16+
        if "torchvision.transforms.functional_tensor" not in sys.modules:
            import types
            import torchvision.transforms.functional as _tvf
            _ft = types.ModuleType("torchvision.transforms.functional_tensor")
            _ft.rgb_to_grayscale = _tvf.rgb_to_grayscale
            sys.modules["torchvision.transforms.functional_tensor"] = _ft

        # Increase recursion limit for SadTalker's deep call chains
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))
        print("[SadTalker] Running GPU lip-sync...")
        from inference import main as sadtalker_main

        # Build args namespace matching SadTalker's ArgumentParser defaults
        import types
        args = types.SimpleNamespace(
            source_image=face_path,
            driven_audio=audio_path,
            checkpoint_dir=checkpoints,
            result_dir=os.path.join(sadtalker_dir, "results"),
            device="cuda" if torch.cuda.is_available() else "cpu",
            still=True,
            preprocess="crop",
            batch_size=2,
            size=256,
            pose_style=0,
            expression_scale=1.0,
            enhancer=None,
            background_enhancer=None,
            ref_eyeblink=None,
            ref_pose=None,
            input_yaw=None,
            input_pitch=None,
            input_roll=None,
            face3dvis=False,
            verbose=False,
            old_version=False,
            net_recon="resnet50",
            init_path=None,
            use_last_fc=False,
            bfm_folder=os.path.join(checkpoints, "BFM_Fitting") + os.sep,
            bfm_model="BFM_model_front.mat",
            focal=1015.0,
            center=112.0,
            camera_d=10.0,
            z_near=5.0,
            z_far=15.0,
        )

        # SadTalker saves video as: <result_dir>/<timestamp>.mp4
        # Capture it by finding the newest mp4 after calling main()
        results_dir = os.path.join(sadtalker_dir, "results")
        before = set()
        if os.path.exists(results_dir):
            before = {f for f in os.listdir(results_dir) if f.endswith(".mp4")}

        sadtalker_main(args)

        after = set()
        if os.path.exists(results_dir):
            after = {f for f in os.listdir(results_dir) if f.endswith(".mp4")}

        new_vids = after - before
        if new_vids:
            newest = os.path.join(results_dir, sorted(new_vids)[-1])
            shutil.move(newest, output_path)
            print(f"[SadTalker] Done: {os.path.basename(output_path)}")
            # Re-encode to H.264 for browser playback
            h264_path = output_path.replace(".mp4", "_h264.mp4")
            ffmpeg = _get_ffmpeg()
            if ffmpeg:
                try:
                    subprocess.run(
                        [ffmpeg, "-y", "-i", output_path,
                         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                         "-c:a", "aac", "-b:a", "128k", h264_path],
                        capture_output=True, check=True,
                    )
                    os.remove(output_path)
                    os.rename(h264_path, output_path)
                    print("[OK] Re-encoded SadTalker output to H.264")
                except Exception as e:
                    print(f"[WARN] H.264 re-encode failed: {e}")
            return output_path

        print("[WARN] SadTalker produced no output video")

    except Exception as e:
        print(f"[WARN] SadTalker failed: {e}")
    finally:
        os.chdir(_prev_dir)

    return None


# ---------------------------------------------------------------------------
# Tier 2 – D-ID API
# ---------------------------------------------------------------------------
def _try_did(face_path: str, audio_path: str, output_path: str) -> str | None:
    global _did_image_url

    headers = {
        "Authorization": f"Basic {DID_API_KEY}",
        "Accept": "application/json",
    }

    try:
        # Upload face image once, cache the URL
        if not _did_image_url:
            print("  [D-ID] Uploading face...")
            with open(face_path, "rb") as f:
                r = requests.post(
                    "https://api.d-id.com/images",
                    headers=headers,
                    files={"image": (os.path.basename(face_path), f, "image/jpeg")},
                    timeout=30,
                )
            if r.status_code != 201:
                print(f"  [ERROR] D-ID image upload failed: {r.status_code} {r.text[:200]}")
                return None
            _did_image_url = r.json()["url"]
            print(f"  [OK] Image uploaded (cached)")

        # Upload audio
        print("  [D-ID] Uploading audio...")
        audio_mime = "audio/wav" if audio_path.endswith(".wav") else "audio/mpeg"
        with open(audio_path, "rb") as f:
            r = requests.post(
                "https://api.d-id.com/audios",
                headers=headers,
                files={"audio": (os.path.basename(audio_path), f, audio_mime)},
                timeout=30,
            )
        if r.status_code != 201:
            print(f"  [ERROR] D-ID audio upload failed: {r.status_code} {r.text[:200]}")
            return None
        audio_url = r.json()["url"]

        # Create talk
        talk_payload = {
            "source_url": _did_image_url,
            "script": {"type": "audio", "audio_url": audio_url},
            "config": {"fluent": False, "pad_audio": 0.0},
        }
        r = requests.post(
            "https://api.d-id.com/talks",
            headers={**headers, "Content-Type": "application/json"},
            json=talk_payload,
            timeout=30,
        )
        if r.status_code not in (200, 201):
            print(f"  [ERROR] D-ID talk creation failed: {r.status_code} {r.text[:200]}")
            return None

        talk_id = r.json()["id"]
        print(f"  [D-ID] Waiting for video (id={talk_id})...")

        # Poll for completion (max 60 s)
        for i in range(30):
            time.sleep(2)
            s = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers, timeout=15)
            data = s.json()
            status = data.get("status", "unknown")
            if status == "done":
                video_url = data.get("result_url")
                # Download video
                vr = requests.get(video_url, timeout=60)
                with open(output_path, "wb") as vf:
                    vf.write(vr.content)
                print(f"  [OK] D-ID lip-sync done: {os.path.basename(output_path)}")
                return output_path
            elif status in ("error", "rejected"):
                print(f"  [ERROR] D-ID generation failed: {data.get('error', status)}")
                return None
            print(f"  [D-ID] status: {status} ({i+1}/30)...")

        print("  [ERROR] D-ID timed out after 60 s")

    except Exception as e:
        print(f"[WARN] D-ID error: {e}")

    return None


# ---------------------------------------------------------------------------
# Tier 3 – Improved OpenCV animation (audio-amplitude driven)
# ---------------------------------------------------------------------------
def _opencv_animate(face_path: str, audio_path: str, output_path: str) -> str:
    # Load audio to get duration and amplitude envelope
    try:
        audio_data, sample_rate = sf.read(audio_path)
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)
        duration = len(audio_data) / sample_rate
    except Exception:
        audio_data = np.zeros(48000)
        sample_rate = 24000
        duration = 2.0

    fps = 30
    total_frames = int(duration * fps)
    # Pre-compute per-frame amplitude (RMS over ~33ms window)
    win = sample_rate // fps
    amplitudes = []
    for i in range(total_frames):
        start = int(i * sample_rate / fps)
        chunk = audio_data[start: start + win]
        rms = float(np.sqrt(np.mean(chunk ** 2))) if len(chunk) > 0 else 0.0
        amplitudes.append(min(rms * 10, 1.0))  # normalise 0-1

    # Load face image
    if os.path.exists(face_path):
        img = cv2.imread(face_path)
    else:
        img = None

    W, H = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, float(fps), (W, H))

    if img is not None:
        # Fit image to frame
        oh, ow = img.shape[:2]
        scale = min(W / ow, H / oh)
        nw, nh = int(ow * scale), int(oh * scale)
        img_r = cv2.resize(img, (nw, nh))
        y0, x0 = (H - nh) // 2, (W - nw) // 2
    else:
        img_r = None

    for i in range(total_frames):
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:] = (15, 15, 25)

        amp = amplitudes[i] if i < len(amplitudes) else 0.0
        t = i / fps

        if img_r is not None:
            # Subtle scale bob tied to amplitude
            sf_val = 1.0 + amp * 0.015 + np.sin(t * 1.5) * 0.003
            sw, sh = int(nw * sf_val), int(nh * sf_val)
            sx0 = x0 - (sw - nw) // 2
            sy0 = y0 - (sh - nh) // 2
            scaled = cv2.resize(img_r, (sw, sh))
            # Clip to frame bounds
            sx0c = max(0, sx0)
            sy0c = max(0, sy0)
            sx1c = min(W, sx0 + sw)
            sy1c = min(H, sy0 + sh)
            isx0 = sx0c - sx0
            isy0 = sy0c - sy0
            if sx1c > sx0c and sy1c > sy0c:
                frame[sy0c:sy1c, sx0c:sx1c] = scaled[isy0:isy0 + (sy1c - sy0c), isx0:isx0 + (sx1c - sx0c)]

        # Talking waveform bar at bottom
        bar_y = H - 12
        for j in range(0, W, 6):
            h_bar = int(amp * 30 * abs(np.sin(t * 8 + j * 0.15)))
            color = (0, int(80 + 175 * amp), int(180 + 75 * amp))
            cv2.line(frame, (j, bar_y), (j, bar_y - h_bar), color, 3)

        # LIVE indicator
        pulse = (np.sin(t * 6) + 1) / 2
        dot_color = (0, int(80 + 175 * pulse), 0)
        cv2.circle(frame, (W - 45, 40), 10, dot_color, -1)
        cv2.putText(frame, "LIVE", (W - 80, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Branding
        alpha = int(200 + 55 * np.sin(t * 2))
        cv2.putText(frame, "EternalBots - Pope Francis", (16, H - 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (alpha, alpha, alpha), 1)
        cv2.putText(frame, "AI Avatar | Powered by XTTS-v2", (16, H - 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (alpha // 2, alpha // 2, alpha // 2), 1)

        writer.write(frame)

    writer.release()
    print(f"[OK] OpenCV fallback animation: {total_frames} frames -> {os.path.basename(output_path)}")

    # Re-encode to H.264 + mux audio so browsers can play it
    h264_path = output_path.replace(".mp4", "_h264.mp4")
    if _mux_audio(output_path, audio_path, h264_path):
        os.remove(output_path)
        os.rename(h264_path, output_path)
        print(f"[OK] Re-encoded to H.264 with audio")

    return output_path
