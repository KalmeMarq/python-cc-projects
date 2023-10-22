import math
import numpy as np

def perspective(fov, aspect_ratio, near_plane, far_plane):
  h = math.tan(fov * 0.5)
  return np.array([
      1.0 / (h * aspect_ratio), 0, 0, 0,
      0, 1.0 / h, 0, 0,
      0, 0, (far_plane + near_plane) / (near_plane - far_plane), -1,
      0, 0, ((far_plane + far_plane) * near_plane) / (near_plane - far_plane), 0
    ])
