from __future__ import annotations
import math
import numpy as np

MAX_SIGNED_INT32 = 2147483647

def clamp(value, min_value, max_value):
  return min_value if value < min_value else max_value if value > max_value else value

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

class AABB:
  def __init__(self, x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> None:
    self.x0 = x0
    self.y0 = y0
    self.z0 = z0
    self.x1 = x1
    self.y1 = y1
    self.z1 = z1

  def __str__(self) -> str:
    return f"AABB[x0={'{:.2f}'.format(self.x0)},y0={'{:.2f}'.format(self.y0)},z0={'{:.2f}'.format(self.z0)},x1={'{:.2f}'.format(self.x1)},y1={'{:.2f}'.format(self.y1)},z1={'{:.2f}'.format(self.z1)}]"

  def intersects(self, aabb: AABB):
    return (aabb.z1 > self.z0 and aabb.z0 < self.z1 if aabb.y1 > self.y0 and aabb.y0 < self.y1 else False) if aabb.x1 > self.x0 and aabb.x0 < self.x1 else False

  def move(self, x, y, z):
    self.x0 += x
    self.y0 += y
    self.z0 += z
    self.x1 += x
    self.y1 += y
    self.z1 += z

  def expand(self, x: float, y: float, z: float):
    x0 = self.x0
    y0 = self.y0
    z0 = self.z0
    x1 = self.x1
    y1 = self.y1
    z1 = self.z1
      
    if x < 0.0:
      x0 += x

    if x > 0.0:
      x1 += x

    if y < 0.0:
      y0 += y

    if y > 0.0:
      y1 += y

    if z < 0.0:
      z0 += z

    if z > 0.0:
      z1 += z

    return AABB(x0, y0, z0, x1, y1, z1)
  
  def grow(self, x, y, z):
    nx0 = self.x0 - x
    ny0 = self.y0 - y
    nz0 = self.z0 - z
    nx1 = self.x1 + x
    ny1 = self.y1 + y
    nz1 = self.z1 + z
    return AABB(nx0, ny0, nz0, nx1, ny1, nz1)
  
  def clipXCollide(self, aabb: AABB, xa: float):
    if aabb.y1 > self.y0 and aabb.y0 < self.y1:
      if aabb.z1 > self.z0 and aabb.z0 < self.z1:
        if xa > 0.0 and aabb.x1 <= self.x0:
          nxa = self.x0 - aabb.x1
          if nxa < xa:
            xa = nxa

        if xa < 0.0 and aabb.x0 >= self.x1:
          nxa = self.x1 - aabb.x0
          if nxa > xa:
            xa = nxa

        return xa
      else:
        return xa
    else:
      return xa
    
  def clipYCollide(self, aabb: AABB, ya: float):
    if aabb.x1 > self.x0 and aabb.x0 < self.x1:
      if aabb.z1 > self.z0 and aabb.z0 < self.z1:
        if ya > 0.0 and aabb.y1 <= self.y0:
          nya = self.y0 - aabb.y1
          if nya < ya:
            ya = nya

        if ya < 0.0 and aabb.y0 >= self.y1:
          nya = self.y1 - aabb.y0
          if nya > ya:
            ya = nya

        return ya
      else:
        return ya
    else:
      return ya
    
  def clipZCollide(self, aabb: AABB, za: float):
    if aabb.x1 > self.x0 and aabb.x0 < self.x1:
      if aabb.y1 > self.y0 and aabb.y0 < self.y1:
        if za > 0.0 and aabb.z1 <= self.z0:
          nza = self.z0 - aabb.z1
          if nza < za:
            za = nza

        if za < 0.0 and aabb.z0 >= self.z1:
          nza = self.z1 - aabb.z0
          if nza > za:
            za = nza

        return za
      else:
        return za
    else:
      return za