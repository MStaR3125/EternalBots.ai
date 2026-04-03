"""Direct SadTalker test with debug output."""
import sys, os, types, traceback

project_root = os.path.dirname(os.path.abspath(__file__))
sadtalker_dir = os.path.join(project_root, "SadTalker")
checkpoints = os.path.join(sadtalker_dir, "checkpoints")

# Check paths
face_path = os.path.join(project_root, "data", "pope_face.jpg")
wav_path = None
tmp = os.path.join(project_root, "tmp")
for f in sorted(os.listdir(tmp)):
    if f.endswith(".wav"):
        wav_path = os.path.join(tmp, f)
        break

print(f"Face path: {face_path}")
print(f"Face exists: {os.path.exists(face_path)}")
print(f"WAV path: {wav_path}")
print(f"WAV exists: {os.path.exists(wav_path) if wav_path else False}")

os.chdir(sadtalker_dir)
if sadtalker_dir not in sys.path:
    sys.path.insert(0, sadtalker_dir)

stub_dir = os.path.join(sadtalker_dir, "pytorch3d_stub")
try:
    import pytorch3d
except ImportError:
    sys.path.insert(0, stub_dir)

# Torchvision compat shim
if "torchvision.transforms.functional_tensor" not in sys.modules:
    import torchvision.transforms.functional as _tvf
    _ft = types.ModuleType("torchvision.transforms.functional_tensor")
    _ft.rgb_to_grayscale = _tvf.rgb_to_grayscale
    sys.modules["torchvision.transforms.functional_tensor"] = _ft

import torch
print(f"CUDA: {torch.cuda.is_available()}")

try:
    from inference import main as sadtalker_main
    args = types.SimpleNamespace(
        source_image=face_path,
        driven_audio=wav_path,
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
    print("Calling SadTalker main()...")
    sadtalker_main(args)
    print("SadTalker main() completed!")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
