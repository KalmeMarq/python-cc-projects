from __future__ import annotations
from OpenGL.GL import *
import math

MAX_SIGNED_INT32 = 2147483647

class VertexDrawer:
  def __init__(self) -> None:
    self.__vertices = 0
    self.__glType = 0

  def begin(self, glType):
    self.__glType = glType

  def flush(self, print_vertices = False):
    if self.__vertices > 0:
      if print_vertices:
        print(self.__vertices)
      glEnd()
    self.__vertices = 0

  def vertex(self, x, y, z):
    if self.__vertices == 0:
      glBegin(self.__glType)

    glVertex3f(x, y, z)
    self.__vertices += 1

  def vertex_uv(self, x, y, z, u, v):
    self.texture(u, v)
    self.vertex(x, y, z)

  def vertex_uv_color(self, x, y, z, u, v, r, g, b, a):
    self.color(r, g, b, a)
    self.texture(u, v)
    self.vertex(x, y, z)

  def color(self, r: float, g: float, b: float, a: float):
    glColor4f(r, g, b, a)
    return self

  def texture(self, u: float, v: float):
    glTexCoord2f(u, v)
    return self

def clamp(value, min_value, max_value):
  return min_value if value < min_value else max_value if value > max_value else value

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
    
class HitResult:
  def __init__(self, bx, by, bz, tile_id, face) -> None:
    self.bx = bx
    self.by = by
    self.bz = bz
    self.tile_id = tile_id
    self.face = face

# Basic unit block based raycast
# https://gamedev.stackexchange.com/questions/47362/cast-ray-to-select-block-in-voxel-game
def bresenham(world, startPoint, endPoint):
  startPoint = [int(startPoint[0]),int(startPoint[1]),int(startPoint[2])]

  endPoint = [int(endPoint[0]),int(endPoint[1]),int(endPoint[2])]

  steepXY = (abs(endPoint[1] - startPoint[1]) > abs(endPoint[0] - startPoint[0]))
  if(steepXY):   
    startPoint[0], startPoint[1] = startPoint[1], startPoint[0]
    endPoint[0], endPoint[1] = endPoint[1], endPoint[0]

  steepXZ = (abs(endPoint[2] - startPoint[2]) > abs(endPoint[0] - startPoint[0]))
  if(steepXZ):
    startPoint[0], startPoint[2] = startPoint[2], startPoint[0]
    endPoint[0], endPoint[2] = endPoint[2], endPoint[0]

  delta = [abs(endPoint[0] - startPoint[0]), abs(endPoint[1] - startPoint[1]), abs(endPoint[2] - startPoint[2])]

  errorXY = delta[0] / 2
  errorXZ = delta[0] / 2

  step = [
    -1 if startPoint[0] > endPoint[0] else 1,
    -1 if startPoint[1] > endPoint[1] else 1,
    -1 if startPoint[2] > endPoint[2] else 1
  ]

  y = startPoint[1]
  z = startPoint[2]

  for x in range(startPoint[0], endPoint[0], step[0]):
    point = [x, y, z]

    if(steepXZ):
        point[0], point[2] = point[2], point[0]
    if(steepXY):
        point[0], point[1] = point[1], point[0]

    tile_id = world.get_tile(point[0], point[1], point[2])
    if tile_id != 0 and tile_id != 7:
      return HitResult(point[0], point[1], point[2], tile_id, 0)

    errorXY -= delta[1]
    errorXZ -= delta[2]

    if(errorXY < 0):
        y += step[1]
        errorXY += delta[0]

    if(errorXZ < 0):
        z += step[2]
        errorXZ += delta[0]
  return None

# https://gamedev.stackexchange.com/questions/47362/cast-ray-to-select-block-in-voxel-game

def signum(x):
  return 1 if x > 0 else -1 if x < 0 else 0

def mod(value, modulus):
  return (value % modulus + modulus) % modulus

def intbound(s, ds):
  return math.ceil(s) - s if ds > 0 else s - math.floor(s) / abs(ds)

def raycast(world, start_pos, direction, reach):
  x = math.floor(start_pos[0])
  y = math.floor(start_pos[1])
  z = math.floor(start_pos[2])

  dx = direction[0]
  dy = direction[1]
  dz = direction[2]
  
  stepX = signum(dx)
  stepY = signum(dy)
  stepZ = signum(dz)

  tMaxX = intbound(start_pos[0], dx)
  tMaxY = intbound(start_pos[1], dy)
  tMaxZ = intbound(start_pos[2], dz)

  tDeltaX = stepX / dx
  tDeltaY = stepY / dy
  tDeltaZ = stepZ / dz

  face = [0.0, 0.0, 0.0]

  if dx == 0 and dy == 0 and dz == 0:
    raise Exception("Raycast in zero direction!")
  
  reach /= math.sqrt(dx * dx + dy * dy + dz * dz)

  wx = world.x_chunks * 16
  wy = 64
  wz = world.z_chunks * 16

  while (
    x < wx if stepX > 0 else x >= 0 and
    y < wy if stepY > 0 else y >= 0 and
    z < wz if stepZ > 0 else z >= 0
  ):
    if not (x < 0 or y < 0 or z < 0 or x >= wx or y >= wy or z >= wz):
      tile_id = world.get_tile(int(x), int(y), int(z))
      if tile_id != 0:
      # if (callback(x, y, z, blocks[x*wy*wz + y*wz + z], face))
        return HitResult(int(x), int(y), int(z), tile_id, 0)

    if tMaxX < tMaxY:
      if tMaxX < tMaxZ:
        if tMaxX > reach:
          break
        x += stepX
        tMaxX += tDeltaX
        face[0] = -stepX
        face[1] = 0
        face[2] = 0
      else:
        if tMaxZ > reach:
          break
        z += stepZ
        tMaxZ += tDeltaZ
        face[0] = 0
        face[1] = 0
        face[2] = -stepZ
    else:
      if tMaxY < tMaxZ:
        if tMaxY > reach:
          break
        y += stepY
        tMaxY += tDeltaY
        face[0] = 0
        face[1] = -stepY
        face[2] = 0
      else:
        if tMaxZ > reach:
          break
        z += stepZ
        tMaxZ += tDeltaZ
        face[0] = 0
        face[1] = 0
        face[2] = -stepZ

  return None