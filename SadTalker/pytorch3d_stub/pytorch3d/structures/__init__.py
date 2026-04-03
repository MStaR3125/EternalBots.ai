import torch

class Meshes:
    def __init__(self, verts=None, faces=None, textures=None):
        self.verts = verts
        self.faces = faces
    def faces_packed(self):
        if self.faces is not None:
            f = self.faces
            if f.dim() == 3:
                return f[0]
            return f
        return torch.zeros(0, 3, dtype=torch.long)
