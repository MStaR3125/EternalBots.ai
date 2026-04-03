# Minimal pytorch3d stub for SadTalker compatibility
# The face coefficients (used by SadTalker) come from net_recon, not the renderer.
# This stub lets the import succeed; the renderer returns zero tensors.
from . import ops, structures, renderer
