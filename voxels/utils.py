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

def signum(value):
  return 1 if value > 0 else -1 if value < 0 else 0

def mod(value, modulus):
  return (value % modulus + modulus) % modulus;

def intbound(s, ds):
  if ds < 0:
    return intbound(-s, -ds)
  else:
    s = mod(s, 1);
    return (1 - s) / ds