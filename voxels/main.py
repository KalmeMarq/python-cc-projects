from __future__ import annotations
import glfw
from typing import Dict
from OpenGL.GL import *
import PIL.Image as Image
import math
import utils
from utils import AABB
import numpy as np
import random
import time

DEBUG_PRINTS = False

class TextureManager:
  def __init__(self):
    self.textures: Dict[str, np.uintc] = {}

  def load(self, path: str) -> None:
    im = Image.open("res/" + path);
    imdata = np.frombuffer(im.convert("RGBA").tobytes(), np.uint8)

    txr_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, txr_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, im.width, im.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imdata)
    glBindTexture(GL_TEXTURE_2D, 0)
    self.textures[path] = txr_id

  def get(self, path: str) -> np.uintc:
    return self.textures[path]
    
  def dispose(self) -> None:
    for txr_id in self.textures.values():
      glDeleteTextures([txr_id])

# O código de colisão não foi totalmente feito por mim
# Obtiu por pesquisa e basiado no Minecraft
class Player:
  WIDTH = 0.6
  HEIGHT = 1.8

  def __init__(self, world: World):
    self.world = world
    self.x = 9
    self.y = 20
    self.z = 9
    self.old_x = 0
    self.old_y = 0
    self.old_z = 0
    self.rot_x = 0
    self.rot_y = 0
    self.on_ground = False
    self.xd = 0
    self.yd = 0
    self.zd = 0
    self.is_inside_water = False
    self.bounding_box = AABB(self.x - Player.WIDTH / 2, self.y - Player.HEIGHT / 2, self.z - Player.WIDTH / 2, self.x + Player.WIDTH / 2, self.y + Player.HEIGHT / 2, self.z + Player.WIDTH / 2)

  def reset_pos(self):
    self.x = random.randint(0, 4 * 16)
    self.y = 64
    self.z = random.randint(0, 4 * 16)
    self.bounding_box = AABB(self.x - Player.WIDTH / 2, self.y - Player.HEIGHT / 2, self.z - Player.WIDTH / 2, self.x + Player.WIDTH / 2, self.y + Player.HEIGHT / 2, self.z + Player.WIDTH / 2)

  def tick(self):
    self.old_x = self.x
    self.old_y = self.y
    self.old_z = self.z

    xa = 0.0
    za = 0.0

    if glfw.get_key(self.world.game.window, glfw.KEY_R) != glfw.RELEASE:
      self.reset_pos()

    if glfw.get_key(self.world.game.window, glfw.KEY_W) != glfw.RELEASE:
      za -= 1
    
    if glfw.get_key(self.world.game.window, glfw.KEY_S) != glfw.RELEASE:
      za += 1

    if glfw.get_key(self.world.game.window, glfw.KEY_A) != glfw.RELEASE:
      xa -= 1
    
    if glfw.get_key(self.world.game.window, glfw.KEY_D) != glfw.RELEASE:
      xa += 1

    if glfw.get_key(self.world.game.window, glfw.KEY_SPACE) != glfw.RELEASE and self.on_ground:
      self.yd = 0.12

    camera_pos = [self.x, self.bounding_box.y0, self.z]
    self.is_inside_water = self.world.get_tile(int(camera_pos[0]), int(camera_pos[1]), int(camera_pos[2])) == 7

    mov_speed = 0.005
    if self.on_ground:
      mov_speed = 0.02
    
    if self.is_inside_water:
      mov_speed *= 0.4

    self.move_relative(xa, za, mov_speed)
    self.yd = self.yd - 0.005
    self.move(self.xd, self.yd, self.zd)
    self.xd *= 0.91
    self.yd *= 0.98
    self.zd *= 0.91
    if self.on_ground:
      self.xd *= 0.8
      self.zd *= 0.8

  def move(self, xa: float, ya: float, za: float):
    xa_ini = xa
    ya_ini = ya
    za_ini = za

    cube_boxes = self.world.get_cubes(self.bounding_box.expand(xa, ya, za))

    for i in range(len(cube_boxes)):
      ya = cube_boxes[i].clipYCollide(self.bounding_box, ya)
    
    self.bounding_box.move(0.0, ya, 0.0)

    for i in range(len(cube_boxes)):
      xa = cube_boxes[i].clipXCollide(self.bounding_box, xa)
    
    self.bounding_box.move(xa, 0.0, 0.0)

    for i in range(len(cube_boxes)):
      za = cube_boxes[i].clipZCollide(self.bounding_box, za)

    self.bounding_box.move(0.0, 0.0, za)

    self.on_ground = ya_ini != ya and ya_ini < 0.0

    if xa_ini != xa:
      self.xd = 0.0

    if ya_ini != ya:
      self.yd = 0.0

    if za_ini != za:
      self.zd = 0.0

    self.x = (self.bounding_box.x0 + self.bounding_box.x1) / 2.0
    self.y = self.bounding_box.y0 + 1.62
    self.z = (self.bounding_box.z0 + self.bounding_box.z1) / 2.0

  def move_relative(self, xa, za, speed):
    dist = xa * xa + za * za
    if dist >= 0.01:
      dist = speed / math.sqrt(dist)
      xa *= dist
      za *= dist

      psin = math.sin(self.rot_y * math.pi / 180.0);
      pcos = math.cos(self.rot_y * math.pi / 180.0);

      self.xd += xa * pcos - za * psin
      self.zd += za * pcos + xa * psin

  def turn(self, xr, yr):
    self.rot_y = self.rot_y + xr * 0.15
    self.rot_x = self.rot_x - yr * 0.15

    if self.rot_x < -90.0:
      self.rot_x = -90.0

    if self.rot_x > 90.0:
      self.rot_x = 90.

TILE_TYPES: Dict[int, TileType] = {}

class TileType:
  def __init__(self, tile_id: int, down_txr: int, up_txr: int, north_txr: int, south_txr: int, west_txr: int, east_txr: int, is_tickable = False) -> None:
    self.tile_id = tile_id
    self.down_txr = down_txr
    self.up_txr = up_txr
    self.north_txr = north_txr
    self.south_txr = south_txr
    self.west_txr = west_txr
    self.east_txr = east_txr
    self.is_tickable = False 

  def render_in_gui(self, vertex_drawer: VertexDrawer):
    tile = self.tile_id
    x0 = 0.0
    y0 = 0.0
    z0 = 0.0
    x1 = 1.0
    y1 = 1.0
    z1 = 1.0

    if tile == 7:
      y1 -= 0.1

    u = (self.down_txr % 3) * 16
    v = self.down_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z0, u0, v0)
    vertex_drawer.vertex_uv(x1, y0, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)

    u = (self.up_txr % 3) * 16
    v = self.up_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(1.0, 1.0, 1.0, 1.0)
    vertex_drawer.vertex_uv(x1, y1, z1, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x0, y1, z1, u0, v1)

    u = (self.north_txr % 3) * 16
    v = self.north_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0
    
    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x1, y0, z0, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z0, u1, v1)

    u = (self.south_txr % 3) * 16
    v = self.south_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z1, u0, v0)
    vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z1, u1, v0)

    u = (self.west_txr % 3) * 16
    v = self.west_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z1, u1, v0)
    vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x0, y0, z0, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z1, u1, v1)

    u = (self.east_txr % 3) * 16
    v = self.east_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
    vertex_drawer.vertex_uv(x1, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x1, y0, z0, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y1, z1, u0, v0)

  def random_tick(self, world: World, x, y, z, tile_id):
    if tile_id == 7:
      if world.get_tile(x - 1, y, z) == 0:
        world.set_tile(x - 1, y, z, 7)

      if world.get_tile(x + 1, y, z) == 0:
        world.set_tile(x + 1, y, z, 7)

      if world.get_tile(x, y, z - 1) == 0:
        world.set_tile(x, y, z - 1, 7)

      if world.get_tile(x, y, z + 1) == 0:
        world.set_tile(x, y, z + 1, 7)

      if world.get_tile(x, y - 1, z) == 0:
        world.set_tile(x, y - 1, z, 7)

TILE_TYPES[1] = TileType(1, 1, 3, 0, 0, 0, 0) # GRASS BLOCK
TILE_TYPES[2] = TileType(2, 1, 1, 1, 1, 1, 1) # DIRT
TILE_TYPES[3] = TileType(3, 4, 4, 4, 4, 4, 4) # STONE
TILE_TYPES[4] = TileType(4, 2, 2, 5, 5, 5, 5) # LOG
TILE_TYPES[5] = TileType(5, 6, 6, 6, 6, 6, 6) # PLANKS
TILE_TYPES[6] = TileType(6, 7, 7, 7, 7, 7, 7) # SAND
TILE_TYPES[7] = TileType(7, 8, 8, 8, 8, 8, 8) # WATER
TILE_TYPES[8] = TileType(8, 11, 11, 11, 11, 11, 11) # LEAVES
TILE_TYPES[9] = TileType(10, 9, 9, 9, 9, 9, 9) # FLOWER

CHUNK_HEIGHT = 64

class RenderLayer:
  def __init__(self, index: int, begin_callback, end_callback) -> None:
    self.__value = index
    self.__begin_callback = begin_callback
    self.__end_callback = end_callback

  def begin(self):
    self.__begin_callback()

  def end(self):
    self.__end_callback()

  @property
  def value(self):
    return self.__value

  def begin_solid_phase():
    glDisable(GL_BLEND)

  def end_solid_phase():
    pass

  def begin_translucent_phase():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  def end_translucent_phase():
    glDisable(GL_BLEND)

  def __eq__(self, __value: object) -> bool:
    return isinstance(__value, RenderLayer) and __value.value == self.value

RenderLayers = {
  'SOLID': RenderLayer(0, RenderLayer.begin_solid_phase, RenderLayer.end_solid_phase),
  'TRANSLUCENT': RenderLayer(1, RenderLayer.begin_translucent_phase, RenderLayer.end_translucent_phase)
}

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

class Chunk:
  def __init__(self, world: World, x: int, z: int):
    self.x = x
    self.z = z
    self.world = world
    self.blocks = [0] * (16 * 16 * CHUNK_HEIGHT)
    self.list = glGenLists(2)
    self.generate()
    self.__dirty = True
    self.light_heightmap = [0] * (16 * 16)
    self.calculate_light_heightmap(0, 0, 16, 16)

  def calculate_light_heightmap(self, x0, z0, x1, z1):
    for x in range(x0, x1):
      for z in range(z0, z1):
        for y in range(CHUNK_HEIGHT - 1, -1, -1):
          tile = self.get_tile(x, y, z)
          if tile != 0:
            self.light_heightmap[(z * 16) + x] = y
            break

  def is_lighted(self, x, y, z) -> bool:
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return True
    return self.light_heightmap[(z * 16) + x] >= y

  def make_dirty(self):
    self.__dirty = True

  def generate(self):
    for x in range(16):
      for y in range(CHUNK_HEIGHT):
        for z in range(16):
          if y > 32:
            continue
          elif y == 0:
            self.blocks[(y * 16 + z) * 16 + x] = 3
          elif y < 5:
            self.blocks[(y * 16 + z) * 16 + x] = 2 if random.randint(0, 17) - y < 1 else 3
          elif y < 15:
            self.blocks[(y * 16 + z) * 16 + x] = 2
          elif y == 15:
            self.blocks[(y * 16 + z) * 16 + x] = 1

    if random.randint(0, 200) < 150:
      randpos_x = random.randint(0, 10)
      randpos_z = random.randint(0, 10)

      if self.get_tile(randpos_x + 2, 15, randpos_z + 2) == 7:
        return

      self.set_tile(randpos_x + 2, 16, randpos_z + 2, 4, calculate_lights=False)
      self.set_tile(randpos_x + 2, 17, randpos_z + 2, 4, calculate_lights=False)
      self.set_tile(randpos_x + 2, 18, randpos_z + 2, 4, calculate_lights=False)
      self.set_tile(randpos_x + 2, 19, randpos_z + 2, 4, calculate_lights=False)

      for tx in range(randpos_x, randpos_x + 5):
        for tz in range(randpos_z, randpos_z + 5):
          self.set_tile(tx, 20, tz, 8, calculate_lights=False)

      for tx in range(randpos_x + 1, randpos_x + 4):
        for tz in range(randpos_z + 1, randpos_z + 4):
          self.set_tile(tx, 21, tz, 8, calculate_lights=False)

  def set_tile(self, x: int, y: int, z: int, tile_id: int, calculate_lights=True):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return
    self.blocks[(y * 16 + z) * 16 + x] = tile_id
    self.__dirty = True
    if calculate_lights:
      self.calculate_light_heightmap(x, z, x + 1, z + 1)

  def get_tile(self, x: int, y: int, z: int):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return 0
    return self.blocks[(y * 16 + z) * 16 + x]

  def rebuild_geometry(self, layer: RenderLayer, world: World, texture_manager: TextureManager):
    glNewList(self.list + layer.value, GL_COMPILE)

    vertex_drawer = VertexDrawer()
    vertex_drawer.begin(GL_QUADS)

    for y in range(CHUNK_HEIGHT):
      for x in range(16):
        for z in range(16):
          bx = x + self.x * 16
          by = y
          bz = z + self.z * 16

          tile = world.get_tile(bx, by, bz)
          if tile < 1 or ((tile == 7) and layer == RenderLayers['SOLID']):
            continue

          tile_type = TILE_TYPES[tile]

          x0 = bx
          y0 = by
          z0 = bz
          x1 = bx + 1.0
          y1 = by + 1.0
          z1 = bz + 1.0

          if tile == 7 and world.get_tile(bx, by + 1, bz) != 7:
            y1 -= 0.1

          temp_tile = world.get_tile(bx, by - 1, bz)
          if tile == 8 or temp_tile == 0 or temp_tile == 8 or (temp_tile == 7 and tile != 7):
            light_multiplier = 1.0
            if world.is_lighted(bx, by - 1, bz):
              light_multiplier = 0.4

            u = (tile_type.down_txr % 3) * 16
            v = tile_type.down_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.6 * light_multiplier, 0.6 * light_multiplier, 0.6 * light_multiplier, 1.0)
            vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
            vertex_drawer.vertex_uv(x0, y0, z0, u0, v0)
            vertex_drawer.vertex_uv(x1, y0, z0, u1, v0)
            vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)

          temp_tile = world.get_tile(bx, by + 1, bz)
          if tile == 8 or temp_tile == 0 or temp_tile == 8 or (temp_tile == 7 and tile != 7) or (tile == 7 and temp_tile != 7):
            light_multiplier = 1.0
            if world.is_lighted(bx, by + 1, bz):
              light_multiplier = 0.4
            
            u = (tile_type.up_txr % 3) * 16
            v = tile_type.up_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(1.0 * light_multiplier, 1.0 * light_multiplier, 1.0 * light_multiplier, 1.0)
            vertex_drawer.vertex_uv(x1, y1, z1, u1, v1)
            vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
            vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
            vertex_drawer.vertex_uv(x0, y1, z1, u0, v1)

          temp_tile = world.get_tile(bx, by, bz - 1)
          if tile == 8 or temp_tile == 0 or temp_tile == 8 or (temp_tile == 7 and tile != 7):
            light_multiplier = 1.0
            if world.is_lighted(bx, by, bz - 1):
              light_multiplier = 0.4
            
            u = (tile_type.north_txr % 3) * 16
            v = tile_type.north_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0
            
            vertex_drawer.color(0.6 * light_multiplier, 0.6 * light_multiplier, 0.6 * light_multiplier, 1.0)
            vertex_drawer.vertex_uv(x0, y1, z0, u1, v0)
            vertex_drawer.vertex_uv(x1, y1, z0, u0, v0)
            vertex_drawer.vertex_uv(x1, y0, z0, u0, v1)
            vertex_drawer.vertex_uv(x0, y0, z0, u1, v1)

          temp_tile = world.get_tile(bx, by, bz + 1)
          if tile == 8 or temp_tile == 0 or temp_tile == 8 or (temp_tile == 7 and tile != 7):
            light_multiplier = 1.0
            if world.is_lighted(bx, by, bz + 1):
              light_multiplier = 0.4

            u = (tile_type.south_txr % 3) * 16
            v = tile_type.south_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.6 * light_multiplier, 0.6 * light_multiplier, 0.6 * light_multiplier, 1.0)
            vertex_drawer.vertex_uv(x0, y1, z1, u0, v0)
            vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
            vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)
            vertex_drawer.vertex_uv(x1, y1, z1, u1, v0)

          temp_tile = world.get_tile(bx - 1, by, bz)
          if tile == 8 or temp_tile == 0 or temp_tile == 8 or (temp_tile == 7 and tile != 7):
            light_multiplier = 1.0
            if world.is_lighted(bx - 1, by, bz):
              light_multiplier = 0.4

            u = (tile_type.west_txr % 3) * 16
            v = tile_type.west_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.8 * light_multiplier, 0.8 * light_multiplier, 0.8 * light_multiplier, 1.0)
            vertex_drawer.vertex_uv(x0, y1, z1, u1, v0)
            vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
            vertex_drawer.vertex_uv(x0, y0, z0, u0, v1)
            vertex_drawer.vertex_uv(x0, y0, z1, u1, v1)

          temp_tile = world.get_tile(bx + 1, by, bz)
          if tile == 8 or temp_tile == 0 or temp_tile == 8 or (temp_tile == 7 and tile != 7):
            light_multiplier = 1.0
            if world.is_lighted(bx + 1, by, bz):
              light_multiplier = 0.4

            u = (tile_type.east_txr % 3) * 16
            v = tile_type.east_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.8 * light_multiplier, 0.8 * light_multiplier, 0.8 * light_multiplier, 1.0)
            vertex_drawer.vertex_uv(x1, y0, z1, u0, v1)
            vertex_drawer.vertex_uv(x1, y0, z0, u1, v1)
            vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
            vertex_drawer.vertex_uv(x1, y1, z1, u0, v0)
          
    vertex_drawer.flush()
    glEndList()   

  def render_debug(self, vertex_drawer = VertexDrawer()):
    clx0 = self.x * 16
    clz0 = self.z * 16
    clx1 = clx0 + 16
    clz1 = clz0 + 16

    vertex_drawer.begin(GL_LINES)
    vertex_drawer.color(1.0, 0.0, 0.0, 1.0)

    vertex_drawer.vertex(clx0, 0, clz0)
    vertex_drawer.vertex(clx0, CHUNK_HEIGHT, clz0)

    vertex_drawer.vertex(clx1, 0, clz0)
    vertex_drawer.vertex(clx1, CHUNK_HEIGHT, clz0)

    vertex_drawer.vertex(clx0, 0, clz1)
    vertex_drawer.vertex(clx0, CHUNK_HEIGHT, clz1)

    vertex_drawer.vertex(clx1, 0, clz1)
    vertex_drawer.vertex(clx1, CHUNK_HEIGHT, clz1)

    for y in range(0, int(CHUNK_HEIGHT / 8)):
      vertex_drawer.color(1.0, 1.0, 0.0, 1.0)
      vertex_drawer.vertex(clx0, y * 8, clz0)
      vertex_drawer.vertex(clx1, y * 8, clz0)
      vertex_drawer.vertex(clx0, y * 8, clz0)
      vertex_drawer.vertex(clx0, y * 8, clz1)
      vertex_drawer.vertex(clx0, y * 8, clz0)
      vertex_drawer.vertex(clx0, y * 8, clz1)

    vertex_drawer.flush()

  def rebuild_layers(self, texture_manager: TextureManager):
    start_time = time.time()
    self.rebuild_geometry(RenderLayers['SOLID'], self.world, texture_manager)
    self.rebuild_geometry(RenderLayers['TRANSLUCENT'], self.world, texture_manager)
    end_time = time.time()
    if DEBUG_PRINTS:
      print(f"DEBUG: Chunk [{self.x}, {self.z}] took {(end_time - start_time) * 1000} ms")
    self.__dirty = False

  def __tick_some_block(self):
    for x in range(0, 16):
        for y in range(0, CHUNK_HEIGHT):
          for z in range(0, 16):
             tile_id = self.blocks[(y * 16 + z) * 16 + x]
             if tile_id == 0:
                continue
             tile_type = TILE_TYPES[tile_id]
             if tile_type.is_tickable:
                print("tickable")
                TILE_TYPES[tile_id].random_tick(self.world, x + self.x * 16, y, z + self.z * 16, tile_id)
                return
             

  def tick(self):
    for _ in range(0, random.randint(0, 2)):
      self.__tick_some_block()

  def render(self, layer: RenderLayer, texture_manager: TextureManager):
    if self.__dirty:
      self.rebuild_layers(texture_manager)
      self.__dirty = False

    glCallList(self.list + layer.value)

  def dispose(self):
    glDeleteLists(self.list, 2)

class World:
  def __init__(self, game: Game):
    self.game = game
    self.x_chunks = 4
    self.z_chunks = 4
    self.chunks: list[Chunk] = []
    self.game.player = Player(self)
    self.border_clist = glGenLists(2)
    self.border_clist_dirty = True
    for x in range(0, self.x_chunks):
      for z in range(0, self.z_chunks):
        self.chunks.append(Chunk(self, x, z))

    for x in range(0, 8):
      for z in range(0, 8):
        self.set_tile(x, 15, z, 7)

    for x in range(0, 7):
      for z in range(0, 7):
        self.set_tile(x, 14, z, 7)
    
    for x in range(0, 5):
      for z in range(0, 6):
        self.set_tile(x, 13, z, 7)

    for chunk in self.chunks:
      chunk.rebuild_layers(game.texture_manager)

  def get_chunk(self, x: int, z: int):
    if x < 0 or x >= self.x_chunks or z < 0 or z >= self.z_chunks:
      return None
    return self.chunks[x * 2 + z]

  def set_tile(self, x: int, y: int, z: int, tile_id: int):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return
    self.chunks[cx * 2 + cz].set_tile(x % 16, y, z % 16, tile_id)
    if x == 0:
      chunknb = self.get_chunk(cx - 1, cz)
      if chunknb != None:
        chunknb.make_dirty()

    if x == 15:
      chunknb = self.get_chunk(cx + 1, cz)
      if chunknb != None:
        chunknb.make_dirty()

    if z == 0:
      chunknb = self.get_chunk(cx, cz - 1)
      if chunknb != None:
        chunknb.make_dirty()
    
    if z == 15:
      chunknb = self.get_chunk(cx, cz + 1)
      if chunknb != None:
        chunknb.make_dirty()

  def is_lighted(self, x, y, z):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return True
    return self.chunks[cx * 2 + cz].is_lighted(x % 16, y, z % 16)

  def get_tile(self, x: int, y: int, z: int):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return 0
    return self.chunks[cx * 2 + cz].get_tile(x % 16, y, z % 16)

  def tick(self):
    chunk_to_update = random.randint(-5, len(self.chunks) - 1)
    if chunk_to_update >= 0:
      self.chunks[chunk_to_update].tick()

  def render(self):
    glDisable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP)
    glFogfv(GL_FOG_COLOR, [0.239, 0.686, 0.807, 1])
    
    camera_pos = self.game.get_camera_pos()
    if self.get_tile(int(camera_pos[0]), int(camera_pos[1]), int(camera_pos[2])) == 7:
      glFogf(GL_FOG_DENSITY, 0.5)
    else:
      glFogf(GL_FOG_DENSITY, 0.07 if self.game.fog_distance == 1 else 0.04 if self.game.fog_distance == 2 else 0.007)
    RenderLayers['SOLID'].begin()

    if self.border_clist_dirty:
      glNewList(self.border_clist, GL_COMPILE)
      
      vertex_drawer = VertexDrawer()
      
      vertex_drawer.begin(GL_QUADS)
      vertex_drawer.color(1.0, 1.0, 1.0, 1.0)
      vertex_drawer.vertex_uv(0, 100, 64, 0, 1)
      vertex_drawer.vertex_uv(0, 100, 0, 0, 0)
      vertex_drawer.vertex_uv(64, 100, 0, 1, 0)
      vertex_drawer.vertex_uv(64, 100, 64, 1, 1)
      
      vertex_drawer.flush()
      
      glEndList()

      wu0 = 32 / 48.0
      wu1 = (32 + 2000) / 48.0
      wv0 = 32 / 64.0
      wv1 = (32 + 2000) / 64.0

      glNewList(self.border_clist + 1, GL_COMPILE)
      vertex_drawer.vertex_uv(0, 15, 1000, wu1, wv1)
      vertex_drawer.vertex_uv(0, 15, -1000, wu1, wv0)
      vertex_drawer.vertex_uv(-1000, 15, -1000, wu0, wv0)
      vertex_drawer.vertex_uv(-1000, 15, 1000, wu0, wv1)

      vertex_drawer.flush()

      glEndList()


      self.border_clist_dirty = False

    glBindTexture(GL_TEXTURE_2D, self.game.texture_manager.get("prof.png"))  
    glCallList(self.border_clist)
    glBindTexture(GL_TEXTURE_2D, self.game.texture_manager.get("grass.png"))
    glCallList(self.border_clist + 1)

    for chunk in self.chunks:
      chunk.render(layer=RenderLayers['SOLID'], texture_manager=self.game.texture_manager)
    
    if self.game.show_debug:
      for chunk in self.chunks:
        chunk.render_debug()

    RenderLayers['SOLID'].end()

    RenderLayers['TRANSLUCENT'].begin()
    for chunk in self.chunks:
      chunk.render(layer=RenderLayers['TRANSLUCENT'], texture_manager=self.game.texture_manager)
    glDisable(GL_BLEND)
    glDisable(GL_FOG)

    RenderLayers['TRANSLUCENT'].end()

  def dispose(self):
    glDeleteLists(self.border_clist, 2)
    for chunk in self.chunks:
      chunk.dispose()

  def get_cubes(self, aabb):
    boxes: list[AABB] = []

    x0 = utils.clamp(int(aabb.x0), 0, self.x_chunks * 16)
    y0 = utils.clamp(int(aabb.y0), 0, utils.MAX_SIGNED_INT32)
    z0 = utils.clamp(int(aabb.z0), 0, self.z_chunks * 16)
    x1 = utils.clamp(int(aabb.x1 + 1), 0, self.x_chunks * 16)
    y1 = utils.clamp(int(aabb.y1 + 1), 0, CHUNK_HEIGHT)
    z1 = utils.clamp(int(aabb.z1 + 1), 0, self.z_chunks * 16)

    for x in range(x0, x1):
      for y in range(y0, y1):
        for z in range(z0, z1):
          tile_id = self.get_tile(x, y, z)
          if tile_id != 0 and tile_id != 7:
            boxes.append(AABB(x, y, z, x + 1, y + 1, z + 1))

    return boxes

class Menu:
  def __init__(self, game: Game) -> None:
    self.game = game
    self.buttons = []
    self.init_gui()

  def resize(self):
    self.buttons.clear()
    self.init_gui()
  
  def init_gui(self):
    pass

  def add_button(self, pos: tuple[int, int], size: tuple[int, int], text: str, callback):
    self.buttons.append((pos, size, text, callback))

  def mouse_clicked(self, mouse_pos: tuple[int, int]):
    for button in self.buttons:
      hovered = mouse_pos[0] > button[0][0] and mouse_pos[0] <= button[0][0] + button[1][0] and mouse_pos[1] > button[0][1] and mouse_pos[1] <= button[0][1] + button[1][1]
      if hovered:
        button[3]()
        break

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    for button in self.buttons:
      hovered = mouse_pos[0] > button[0][0] and mouse_pos[0] <= button[0][0] + button[1][0] and mouse_pos[1] > button[0][1] and mouse_pos[1] <= button[0][1] + button[1][1]
      game.draw_texture_nineslice("gui.png", button[0], button[1], (20 if hovered else 0, 22), (20, 20), (4, 4, 4, 4), 256, 64)
      game.draw_text(button[2], button[0][0] + button[1][0] / 2, button[0][1] + 6, 0xFFFFFF, 0.5)

class MainMenu(Menu):
  def init_gui(self):
    self.add_button((self.game.width / 4 - 100, self.game.height / 4 - 24), (200, 20), "PLAY GAME", self.__play)
    self.add_button((self.game.width / 4 - 100, self.game.height / 4), (200, 20), "QUIT", self.game.shutdown)
  
  def __play(self):
    self.game.start_world()

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    game.draw_texture(texture_name="bg.png", x=0, y=0, width=game.width / 2, height=game.height / 2, u=0, v=0, us=game.width / 2, vs=game.height / 2, tw=16, th=16, color=0x666666)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    super().render(game, mouse_pos)
    game.draw_text("VOXELS", 1, 1, 0xFFFFFF, 0)

class LoadingTerrainMenu(Menu):
  def __init__(self, game: Game) -> None:
    super().__init__(game)
    self.started = False

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    game.draw_texture(texture_name="bg.png", x=0, y=0, width=game.width / 2, height=game.height / 2, u=0, v=0, us=game.width / 2, vs=game.height / 2, tw=16, th=16, color=0x666666)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    super().render(game, mouse_pos)
    game.draw_text("GENERATING TERRAIN...", self.game.width / 4, 40, 0xFFFFFF, 0.5)

    if self.started:
      self.game.world = World(self.game)
      self.game.grab_mouse()
      self.game.menu = None

    if not self.started:
      self.started = True

class PauseMenu(Menu):
  def init_gui(self):
    self.add_button((self.game.width / 4 - 100, self.game.height / 4 - 48), (200, 20), "CONTINUE GAME", self.__play)
    self.add_button((self.game.width / 4 - 100, self.game.height / 4 - 24), (200, 20), "RETURN TO TITLE", self.__return_main)

  def __play(self):
    self.game.menu = None
    self.game.grab_mouse()

  def __return_main(self):
    self.game.menu = MainMenu(self.game)

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    game.draw_rect((0, 0), (game.width / 2, game.height / 2), 0x66000000)
    super().render(game, mouse_pos)

class HitResult:
  def __init__(self, bx, by, bz, tile_id, face) -> None:
    self.bx = bx
    self.by = by
    self.bz = bz
    self.tile_id = tile_id
    self.face = face

# Basic unit block based raycast
# https://gamedev.stackexchange.com/questions/47362/cast-ray-to-select-block-in-voxel-game
def bresenham(world: World, startPoint, endPoint):
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

class Game:
  def __init__(self):
    if not glfw.init():
      exit(0)

    self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.!:/"
    self.show_debug = False
    self.width = 700
    self.height = 450

    glfw.default_window_hints()
    self.window = glfw.create_window(self.width, self.height, "Voxels", None, None)
    self.set_icon("icon.png")
    glfw.make_context_current(self.window)
    glfw.swap_interval(1)

    self.texture_manager = TextureManager()
    self.texture_manager.load('grass.png')
    self.texture_manager.load('gui.png')
    self.texture_manager.load('bg.png')
    self.texture_manager.load('prof.png')
    self.current_fps = 0
    self.mouse = {
      'x': 0,
      'y': 0,
      'dx': 0,
      'dy': 0
    }

    self.running = True
    self.player: Player | None = None 
    glfw.set_key_callback(self.window, lambda _,key,scancode,action,mods : self.on_key(key, scancode, action, mods))
    glfw.set_cursor_pos_callback(self.window, lambda _,xpos,ypos : self.on_cursor_pos(xpos, ypos))
    glfw.set_mouse_button_callback(self.window, lambda _,button,action,mods : self.on_mouse_button(button, action, mods))
    glfw.set_framebuffer_size_callback(self.window, lambda _,w,h : self.on_framebuffer_size_changed(w, h))
    glfw.set_scroll_callback(self.window, lambda _w,xoff,yoff : self.on_scroll(xoff, yoff))
    self.menu = MainMenu(self)

    self.world: World | None = None
    self.hit_result: HitResult | None = None
    self.selected_tile = 1
    self.fog_distance = 1

  def start_world(self):
    self.menu = LoadingTerrainMenu(self)

  def shutdown(self):
    self.running = False

  def set_icon(self, path: str):
    imicon = Image.open("res/" + path)
    glfw.set_window_icon(self.window, 1, [imicon])

  def on_scroll(self, xoff, yoff):
    step = 1 if yoff > 0 else -1

    self.selected_tile -= step

    if self.selected_tile < 1:
      self.selected_tile = 9

    if self.selected_tile > 9:
      self.selected_tile = 1

  def on_framebuffer_size_changed(self, width, height):
    self.width = width
    self.height = height
    glViewport(0, 0, self.width, self.height)
    self.proj_mat = utils.perspective(1.22172, self.width / self.height, 0.05, 1000.0)
    if self.menu != None:
      self.menu.resize()

  def on_mouse_button(self, button, action, mods):
    if action == glfw.PRESS and button == 0 and self.menu != None:
      self.menu.mouse_clicked((self.mouse['x'] / 2, self.mouse['y'] / 2))
    
    if action == glfw.PRESS and button == 0 and self.menu == None and self.hit_result != None:
      self.world.set_tile(self.hit_result.bx, self.hit_result.by, self.hit_result.bz, 0)
    
    if action == glfw.PRESS and button == 1 and self.menu == None and self.hit_result != None:
      bx = self.hit_result.bx
      by = self.hit_result.by
      bz = self.hit_result.bz

      # if self.hit_result.face == 0:
      #   by += 1

      # if self.hit_result.face == 1:
      #   by -= 1

      # if self.hit_result.face == 2:
      #   bz -= 2

      # if self.hit_result.face == 3:
      #   bz += 2

      # if self.hit_result.face == 4:
      #   bx += 1

      # if self.hit_result.face == 5:
      #   bx -= 1

      print(self.hit_result.face)

      self.world.set_tile(bx, by, bz, self.selected_tile)

  def on_cursor_pos(self, xpos, ypos):
    self.mouse['dx'] = xpos - self.mouse['x']
    self.mouse['dy'] = self.mouse['y'] - ypos
    self.mouse['x'] = xpos
    self.mouse['y'] = ypos

  def on_key(self, key, scancode, action, mods):
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE and self.menu == None:
      self.menu = PauseMenu(self)
      self.ungrab_mouse()

    if action == glfw.PRESS and key == glfw.KEY_F and self.menu == None:
      self.fog_distance += 1
      if self.fog_distance > 3:
        self.fog_distance = 1

    if action == glfw.PRESS and key == glfw.KEY_F3:
      self.show_debug = not self.show_debug

    if action == glfw.PRESS and (key >= glfw.KEY_1 and key <= glfw.KEY_9):
      self.selected_tile = key - glfw.KEY_0

  def grab_mouse(self):
    glfw.set_cursor_pos(self.window, self.width / 2, self.height / 2)
    glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

  def ungrab_mouse(self):
    glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    glfw.set_cursor_pos(self.window, self.width / 2, self.height / 2)

  def get_camera_pos(self):
    return [self.player.x, self.player.y, self.player.z]

  def run(self):
    glClearColor(0.239, 0.686, 0.807, 1.0)
    last_time = glfw.get_time()
    frame_counter = 0
    self.proj_mat = utils.perspective(1.22172, self.width / self.height, 0.05, 1000.0)
    tick_last_time = glfw.get_time()
    tick_delta = 0

    while self.running:
      if glfw.window_should_close(self.window):
        self.running = False

      tick_now = glfw.get_time()
      tick_passed_sec = tick_now - tick_last_time
      tick_last_time = tick_now
      tick_delta += tick_passed_sec * 60 / 1.0
      ticks = int(tick_delta)
      tick_delta -= ticks

      for _ in range(0, ticks):
        self.tick()

      dx = self.mouse['dx']
      dy = self.mouse['dy']
      if self.menu == None:
        self.player.turn(dx, dy)
      self.mouse['dx'] = 0
      self.mouse['dy'] = 0
      
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

      self.render(tick_delta)
      
      glfw.swap_buffers(self.window)
      glfw.poll_events()

      frame_counter += 1

      now = glfw.get_time()
      if now - last_time > 1.0:
        last_time = now
        self.current_fps = frame_counter
        frame_counter = 0

    if self.world != None:
      self.world.dispose()
    self.texture_manager.dispose()
    glfw.terminate()

  def render(self, tick_delta: float):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glLoadMatrixf(self.proj_mat)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    
    if self.world != None:
      glTranslatef(0, 0, -0.3)
      glRotatef(self.player.rot_x, 1.0, 0.0, 0.0);
      glRotatef(self.player.rot_y, 0.0, 1.0, 0.0);

      player_x = self.player.old_x + (self.player.x - self.player.old_x) * tick_delta
      player_y = self.player.old_y + (self.player.y - self.player.old_y) * tick_delta
      player_z = self.player.old_z + (self.player.z - self.player.old_z) * tick_delta

      glTranslatef(-player_x, -player_y, -player_z)

      start_pos = self.get_camera_pos()
      end_pos = self.get_camera_pos()
      rv0 = math.cos(-self.player.rot_y * (math.pi / 180.0) - math.pi)
      rv1 = math.sin(-self.player.rot_y * (math.pi / 180.0) - math.pi)
      rv2 = -math.cos(-self.player.rot_x * math.pi / 180.0)
      rv3 =-math.sin(-self.player.rot_x * math.pi / 180.0)

      end_pos[0] -= rv1 * rv2 * 7
      end_pos[1] -= rv3 * 7
      end_pos[2] -= rv0 * rv2 * 7

      self.hit_result = bresenham(self.world, start_pos, end_pos)

      glBindTexture(GL_TEXTURE_2D, self.texture_manager.get("grass.png"))  
      self.world.render()

      if self.hit_result != None:
        glDisable(GL_TEXTURE_2D)
        
        selx0 = self.hit_result.bx - 0.005
        sely0 = self.hit_result.by - 0.005
        selz0 = self.hit_result.bz - 0.005
        selx1 = self.hit_result.bx + 1.005
        sely1 = self.hit_result.by + 1.005
        selz1 = self.hit_result.bz + 1.005
        
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        # ver
        glVertex3f(selx0, sely0, selz0)
        glVertex3f(selx0, sely1, selz0)
        glVertex3f(selx1, sely0, selz0)
        glVertex3f(selx1, sely1, selz0)
        glVertex3f(selx1, sely0, selz1)
        glVertex3f(selx1, sely1, selz1)
        glVertex3f(selx0, sely0, selz1)
        glVertex3f(selx0, sely1, selz1)
        # hor
        glVertex3f(selx0, sely0, selz0)
        glVertex3f(selx1, sely0, selz0)

        glVertex3f(selx0, sely0, selz1)
        glVertex3f(selx1, sely0, selz1)

        glVertex3f(selx0, sely0, selz0)
        glVertex3f(selx0, sely0, selz1)

        glVertex3f(selx1, sely0, selz0)
        glVertex3f(selx1, sely0, selz1)

        glVertex3f(selx0, sely1, selz0)
        glVertex3f(selx1, sely1, selz0)

        glVertex3f(selx0, sely1, selz1)
        glVertex3f(selx1, sely1, selz1)

        glVertex3f(selx0, sely1, selz0)
        glVertex3f(selx0, sely1, selz1)

        glVertex3f(selx1, sely1, selz0)
        glVertex3f(selx1, sely1, selz1)
        glEnd()
        glEnable(GL_TEXTURE_2D)

    glClear(GL_DEPTH_BUFFER_BIT)

    scaled_width = self.width / 2
    scaled_height = self.height / 2

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, scaled_width, scaled_height, 0, 1000.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -2000.0)

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ONE_MINUS_SRC_COLOR)
    self.draw_texture("gui.png", scaled_width / 2 - 8, scaled_height / 2 - 8, 16, 16, 240, 0, 16, 16, 256, 64)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    self.draw_texture("gui.png", scaled_width / 2 - 91, scaled_height - 22, 182, 22, 0, 0, 182, 22, 256, 64)
    
    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get("grass.png"))
    glEnable(GL_CULL_FACE)
    glPushMatrix()
    glTranslatef(scaled_width - 45, 80, 20)
    glRotatef(-20, 1, 0, 0)
    glRotatef(44, 0, 1, 0)
    glTranslatef(0, -10, 0)
    glScalef(26, -26, 26)

    tile_type = TILE_TYPES[self.selected_tile]
    vertex_drawer = VertexDrawer()
    vertex_drawer.begin(GL_QUADS)
    tile_type.render_in_gui(vertex_drawer=vertex_drawer)
    vertex_drawer.flush()
    glPopMatrix()
    glDisable(GL_CULL_FACE)

    for i in range(0, 9):
      tile_txr = TILE_TYPES[i + 1].north_txr
      self.draw_texture("grass.png", scaled_width / 2 - 91 + 3 + i * 20, scaled_height - 22 + 3, 16, 16, (tile_txr % 3) * 16, (tile_txr // 3) * 16, 16, 16, 48, 64)

    self.draw_texture("gui.png", scaled_width / 2 - 91 + (self.selected_tile - 1) * 20, scaled_height - 22 - 1, 24, 24, 40, 22, 24, 24, 256, 64)

    glDisable(GL_BLEND)

    if self.menu != None:
      self.menu.render(self, (self.mouse['x'] / 2, self.mouse['y'] / 2))

    if self.world == None:
      return

    self.draw_text("VOXELS", 1, 1, 0xFFFFFF, 0)

    if self.show_debug:
      self.draw_text(f"{self.current_fps} FPS", 1, 11, 0xFFFFFF, 0)
      self.draw_text(f"{'X: {:.4f}'.format(self.player.x)}", 1, 21, 0xFFFFFF, 0)
      self.draw_text(f"{'Y: {:.4f}'.format(self.player.y)}", 1, 31, 0xFFFFFF, 0)
      self.draw_text(f"{'Z: {:.4f}'.format(self.player.z)}", 1, 41, 0xFFFFFF, 0)
      self.draw_text(f"SELECTED TILE: {self.selected_tile}", 1, 51, 0xFFFFFF, 0)
      self.draw_text(f"PYTHON {platform.sys.version_info.major}.{platform.sys.version_info.minor}.{platform.sys.version_info.micro}", scaled_width - 1, 1, 0xFFFFFF, 1)
      self.draw_text(f"DISPLAY: {self.width}X{self.height}", scaled_width - 1, 21, 0xFFFFFF, 1)
    else:
      self.draw_text("PRESS F3 TO SHOW DEBUG", 1, 11, 0xFFFFFF, 0)

  def draw_texture_nineslice(self, texture_name, pos: tuple[int, int], size: tuple[int, int], uv: tuple[int, int], uv_size: tuple[int, int], nineslice: tuple[int, int, int, int], tw: int, th: int):
    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get(texture_name))
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBegin(GL_QUADS) 
    # Top Left
    self.__draw_texture_quad(pos[0], pos[1], nineslice[0], nineslice[1], uv[0], uv[1], nineslice[0], nineslice[1], tw, th)
    # Top Middle
    self.__draw_texture_quad(pos[0] + nineslice[0], pos[1], size[0] - nineslice[0] - nineslice[2], nineslice[1], uv[0] + nineslice[0], uv[1], uv_size[0] - nineslice[0] - nineslice[2], nineslice[1], tw, th)
    # Top Right
    self.__draw_texture_quad(pos[0] + size[0] - nineslice[2], pos[1], nineslice[2], nineslice[1], uv[0] + uv_size[0] - nineslice[2], uv[1], nineslice[2], nineslice[1], tw, th)
    # Left Middle
    self.__draw_texture_quad(pos[0], pos[1] + nineslice[1], nineslice[0], size[1] - nineslice[1] - nineslice[3], uv[0], uv[1] + nineslice[1], nineslice[0], uv_size[1] - nineslice[2] - nineslice[3], tw, th)
    # Center
    self.__draw_texture_quad(pos[0] + nineslice[0], pos[1] + nineslice[1], size[0] - nineslice[0] - nineslice[2], size[1] - nineslice[1] - nineslice[3], uv[0] + nineslice[0], uv[1] + nineslice[1], uv_size[0] - nineslice[0] - nineslice[2], uv_size[1] - nineslice[1] - nineslice[3], tw, th)
    # Right Middle
    self.__draw_texture_quad( pos[0] + size[0] - nineslice[2], pos[1] + nineslice[1], nineslice[2], size[1] - nineslice[1] - nineslice[3], uv[0] + uv_size[0] - nineslice[2], uv[1] + nineslice[1], nineslice[2], uv_size[1] - nineslice[1] - nineslice[3], tw, th)
    # Bottom Left
    self.__draw_texture_quad(pos[0], pos[1] + size[1] - nineslice[3], nineslice[0], nineslice[3], uv[0], uv[1] + uv_size[1] - nineslice[3], nineslice[0], nineslice[3], tw, th)
    # Bottom Middle
    self.__draw_texture_quad(pos[0] + nineslice[0], pos[1] + size[1] - nineslice[3], size[0] - nineslice[0] - nineslice[2], nineslice[3], uv[0] + nineslice[0], uv[1] + uv_size[1] - nineslice[2], uv_size[0] - nineslice[0] - nineslice[2], nineslice[3], tw, th)
    # Bottom Right
    self.__draw_texture_quad(pos[0] + size[0] - nineslice[2], pos[1] + size[1] - nineslice[3], nineslice[2], nineslice[3], uv[0] + uv_size[0] - nineslice[2], uv[1] + uv_size[1] - nineslice[3], nineslice[2], nineslice[3], tw, th)
    glEnd()

  def __draw_texture_quad(self, x: int, y: int, width: int, height: int, u: int, v: int, us: int, vs: int, tw: int, th: int):
    u0 = u / tw
    v0 = v / th
    u1 = (u + us) / tw
    v1 = (v + vs) / th
    
    glTexCoord2f(u0, v0)
    glVertex3f(x, y, 0)
    glTexCoord2f(u0, v1)
    glVertex3f(x, y + height, 0)
    glTexCoord2f(u1, v1)
    glVertex3f(x + width, y + height, 0)
    glTexCoord2f(u1, v0)
    glVertex3f(x + width, y, 0)

  def draw_rect(self, pos: tuple[int, int], size: tuple[int, int], color: int = 0xFFFFFFFF):
    glEnable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f((color >> 16 & 0xFF) / 255.0, (color >> 8 & 0xFF) / 255.0, (color & 0xFF) / 255.0, (color >> 24 & 0xFF) / 255.0)
    glBegin(GL_QUADS)
    glVertex3f(pos[0], pos[1], 0)
    glVertex3f(pos[0], pos[1] + size[1], 0)
    glVertex3f(pos[0] + size[0], pos[1] + size[1], 0)
    glVertex3f(pos[0] + size[0], pos[1], 0)
    glEnd()
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glDisable(GL_BLEND)
    glEnable(GL_TEXTURE_2D)

  def draw_texture(self, texture_name, x: int, y: int, width: int, height: int, u: int, v: int, us: int, vs: int, tw: int, th: int, color: int = 0xFFFFFF):
    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get(texture_name))

    glColor4f((color >> 16 & 0xFF) / 255.0, (color >> 8 & 0xFF) / 255.0, (color & 0xFF) / 255.0, 1.0)
    glBegin(GL_QUADS)
    self.__draw_texture_quad(x, y, width, height, u, v, us, vs, tw, th)
    glEnd()

  def draw_text(self, message: str, x: int, y: int, color: int, align: float):
    self.__draw_text(message, x + 1, y + 1, 0x000000, align)
    self.__draw_text(message, x, y, color, align)

  def __draw_text(self, message: str, x: int, y: int, color: int, align: float):
    glColor4f((color >> 16 & 0xFF) / 255.0, (color >> 8 & 0xFF) / 255.0, (color & 0xFF) / 255.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get("gui.png"))

    glBegin(GL_QUADS)

    xx = x - (len(message) * 8) * align

    for char in message:
      if char == ' ':
        xx += 8
        continue
      
      idx = self.chars.find(char)
      u = (idx % 20) * 8
      v = 48 + (idx // 20) * 8

      u0 = u / 256
      v0 = v / 64
      u1 = (u + 8) / 256
      v1 = (v + 8) / 64

      glTexCoord2f(u0, v0)
      glVertex3f(xx, y, 0)
      glTexCoord2f(u0, v1)
      glVertex3f(xx, y + 8, 0)
      glTexCoord2f(u1, v1)
      glVertex3f(xx + 8, y + 8, 0)
      glTexCoord2f(u1, v0)
      glVertex3f(xx + 8, y, 0)

      xx += 8

    glEnd()

    glDisable(GL_BLEND)

  def tick(self):
    if self.world != None:
      self.world.tick()
      self.player.tick()
      # xa = 0
      # ya = 0
      # za = 0

      # if glfw.get_key(self.window, glfw.KEY_W) != glfw.RELEASE:
      #   za -= 1
      
      # if glfw.get_key(self.window, glfw.KEY_S) != glfw.RELEASE:
      #   za += 1

      # if glfw.get_key(self.window, glfw.KEY_A) != glfw.RELEASE:
      #   xa -= 1
      
      # if glfw.get_key(self.window, glfw.KEY_D) != glfw.RELEASE:
      #   xa += 1

      # if glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) != glfw.RELEASE or glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) != glfw.RELEASE:
      #   ya -= 1
      
      # if glfw.get_key(self.window, glfw.KEY_SPACE) != glfw.RELEASE:
      #   ya += 1

      # xa *= 0.61
      # za *= 0.61

      # psin = math.sin(self.player.rot_y * math.pi / 180.0);
      # pcos = math.cos(self.player.rot_y * math.pi / 180.0);

      # if self.world.get_tile(int(self.player.x), int(self.player.y) - 2, int(self.player.z)) == 0:
      #   ya -= 1
      # else:
      #   ya = 0
  
      # self.player.x += xa * pcos - za * psin
      # self.player.y += ya
      # self.player.z += za * pcos + xa * psin


if __name__ == "__main__":
  game = Game()
  game.run()