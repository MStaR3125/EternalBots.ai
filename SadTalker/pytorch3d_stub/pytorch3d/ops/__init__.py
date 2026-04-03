import torch

def interpolate_face_attributes(pix_to_face, bary_coords, attributes):
    """Stub: returns zeros of plausible shape."""
    B, H, W, K = pix_to_face.shape
    C = attributes.shape[-1] if attributes.dim() > 1 else 3
    return torch.zeros(B, H, W, K, C, device=pix_to_face.device)
