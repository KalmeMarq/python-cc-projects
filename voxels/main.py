from __future__ import annotations
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import utils
from utils import AABB, HitResult, bresenham, VertexDrawer
import random
import time
from textures import TextureManager
from tiles import TILE_TYPES
from render_layers import RenderLayer, RenderLayers
from window import GameWindow
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

DEBUG_PRINTS = False

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

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_R) != glfw.RELEASE:
      self.reset_pos()

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_W) != glfw.RELEASE:
      za -= 1
    
    if glfw.get_key(self.world.game.window.handle, glfw.KEY_S) != glfw.RELEASE:
      za += 1

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_A) != glfw.RELEASE:
      xa -= 1
    
    if glfw.get_key(self.world.game.window.handle, glfw.KEY_D) != glfw.RELEASE:
      xa += 1

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_SPACE) != glfw.RELEASE and self.on_ground:
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

  # O código de colisão não foi totalmente feito por mim
  # Obtiu por pesquisa e basiado no Minecraft
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
      self.rot_x = 90.0

CHUNK_HEIGHT = 64

class Chunk:
  CHUNK_UPDATES = 0

  def __init__(self, world: World, x: int, z: int):
    self.x = x
    self.z = z
    self.world = world
    self.blocks = [0] * (16 * 16 * CHUNK_HEIGHT)
    self.__list = glGenLists(2)
    self.generate()
    self.__dirty = True
    self.__light_heightmap = [0] * (16 * 16)
    self.calculate_light_heightmap(0, 0, 16, 16)

  def calculate_light_heightmap(self, x0, z0, x1, z1):
    for x in range(x0, x1):
      for z in range(z0, z1):
        for y in range(CHUNK_HEIGHT - 1, -1, -1):
          tile = self.get_tile(x, y, z)
          if tile != 0 and not TILE_TYPES[tile].allows_light_through:
            self.__light_heightmap[(z * 16) + x] = y
            break

  def is_lighted(self, x, y, z) -> bool:
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return True
    return self.__light_heightmap[(z * 16) + x] >= y

  def make_dirty(self):
    self.__dirty = True

  def generate(self):
    for x in range(16):
      for y in range(CHUNK_HEIGHT):
        for z in range(16):
          if y > 32:
            continue
          elif y == 0:
            self.blocks[(y * 16 + z) * 16 + x] = 9
          elif y < 10:
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
      if DEBUG_PRINTS:
        print(f"Chunk[x={self.x},z={self.z}] set tile {tile_id} ({x},{y},{z}) ({x + self.x * 16}, {y}, {z + self.z * 16})")
      self.calculate_light_heightmap(x, z, x + 1, z + 1)

  def get_tile(self, x: int, y: int, z: int):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return 0
    return self.blocks[(y * 16 + z) * 16 + x]

  def rebuild_geometry(self, layer: RenderLayer, world: World, texture_manager: TextureManager):
    glNewList(self.__list + layer.value, GL_COMPILE)
    Chunk.CHUNK_UPDATES += 1

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
                TILE_TYPES[tile_id].random_tick(self.world, x + self.x * 16, y, z + self.z * 16, tile_id)
                return
             

  def tick(self):
    for _ in range(0, random.randint(0, 2)):
      self.__tick_some_block()

  def render(self, layer: RenderLayer, texture_manager: TextureManager):
    if self.__dirty:
      self.rebuild_layers(texture_manager)
      if DEBUG_PRINTS:
        print(f"Chunk[x={self.x},z={self.z}] rendered")
      self.__dirty = False

    glCallList(self.__list + layer.value)

  def dispose(self):
    glDeleteLists(self.__list, 2)

class World:
  def __init__(self, game: Game):
    self.game = game
    self.x_chunks = 6
    self.z_chunks = 6
    self.chunks: list[Chunk] = [None] * (self.x_chunks * self.z_chunks)
    self.game.player = Player(self)
    self.border_clist = glGenLists(1)
    self.border_clist_dirty = True

    for x in range(0, self.x_chunks):
      for z in range(0, self.z_chunks):
        self.chunks[x * self.z_chunks + z] = Chunk(self, x, z)

    self.__generate_spawn_water()

    for chunk in self.chunks:
      chunk.rebuild_layers(game.texture_manager)

  def __generate_spawn_water(self):
    for x in range(0, 8):
      for z in range(0, 8):
        self.set_tile(x, 15, z, 7)
        self.set_tile(x, 14, z, 6)

    for x in range(0, 7):
      for z in range(0, 7):
        self.set_tile(x, 14, z, 7)
        self.set_tile(x, 13, z, 6)
    
    for x in range(0, 5):
      for z in range(0, 6):
        self.set_tile(x, 13, z, 7)
        self.set_tile(x, 12, z, 6)
    
  def get_chunk(self, x: int, z: int):
    if x < 0 or x >= self.x_chunks or z < 0 or z >= self.z_chunks:
      return None
    return self.chunks[x * self.z_chunks + z]

  def set_tile(self, x: int, y: int, z: int, tile_id: int):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return
    self.chunks[cx * self.z_chunks + cz].set_tile(x % 16, y, z % 16, tile_id)
    if (x % 16) == 0:
      chunknb = self.get_chunk(cx - 1, cz)
      if chunknb != None:
        chunknb.make_dirty()

    if (x % 16) == 15:
      chunknb = self.get_chunk(cx + 1, cz)
      if chunknb != None:
        chunknb.make_dirty()

    if (z % 16) == 0:
      chunknb = self.get_chunk(cx, cz - 1)
      if chunknb != None:
        chunknb.make_dirty()
    
    if (z % 16) == 15:
      chunknb = self.get_chunk(cx, cz + 1)
      if chunknb != None:
        chunknb.make_dirty()

  def is_lighted(self, x, y, z):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return True
    return self.chunks[cx * self.z_chunks + cz].is_lighted(x % 16, y, z % 16)

  def get_tile(self, x: int, y: int, z: int):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return 0
    return self.chunks[cx * self.z_chunks + cz].get_tile(x % 16, y, z % 16)

  def tick(self):
    chunk_to_update = random.randint(-15, len(self.chunks) - 1)
    if chunk_to_update >= 0:
      self.chunks[chunk_to_update].tick()

  def render(self):
    glEnable(GL_FOG)
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
      vertex_drawer.vertex_uv_color(0, 70, 64, 0, 1, 1.0, 0.0, 0.0, 1.0)
      vertex_drawer.vertex_uv_color(0, 70, 0, 0, 0, 0.0, 1.0, 0.0, 1.0)
      vertex_drawer.vertex_uv_color(64, 70, 0, 1, 0, 0.0, 0.0, 1.0, 1.0)
      vertex_drawer.vertex_uv_color(64, 70, 64, 1, 1, 1.0, 0.0, 1.0, 1.0)
      
      vertex_drawer.flush()
      
      glEndList()

      self.border_clist_dirty = False

    for chunk in self.chunks:
      chunk.render(layer=RenderLayers['SOLID'], texture_manager=self.game.texture_manager)
    
    if self.game.show_debug:
      for chunk in self.chunks:
        chunk.render_debug()

    RenderLayers['SOLID'].end()

    if self.game.show_debug:
      self.game.texture_manager.get("prof.png").bind()  
      glCallList(self.border_clist)
      glPushMatrix()
      glDisable(GL_CULL_FACE)
      glTranslatef(16, 69, 16)
      glRotatef(90, 1, 0, 0)
      glRotatef(180, 0, 1, 0)
      self.game.font.draw_text("BRUH", 0, 0, 0xFFFFFF, 0, shadow=False)
      glPopMatrix()
      glEnable(GL_CULL_FACE)
      self.game.texture_manager.get("grass.png").bind()
    
    RenderLayers['TRANSLUCENT'].begin()
    # glDisable(GL_CULL_FACE)
    for chunk in self.chunks:
      chunk.render(layer=RenderLayers['TRANSLUCENT'], texture_manager=self.game.texture_manager)
    RenderLayers['TRANSLUCENT'].end()
    # glEnable(GL_CULL_FACE)
    glDisable(GL_FOG)

  def dispose(self):
    glDeleteLists(self.border_clist, 1)
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
    self.buttons.append([pos, size, text, callback])

  def mouse_clicked(self, mouse_pos: tuple[int, int]):
    for button in self.buttons:
      hovered = mouse_pos[0] > button[0][0] and mouse_pos[0] <= button[0][0] + button[1][0] and mouse_pos[1] > button[0][1] and mouse_pos[1] <= button[0][1] + button[1][1]
      if hovered:
        self.game.play_sound(self.game.click_sound)
        button[3]()
        break

  def render_dirt_bg(self):
    game.draw_texture(texture_name="bg.png", x=0, y=0, width=self.game.window.scaled_width(), height=self.game.window.scaled_height(), u=0, v=0, us=self.game.window.scaled_width(), vs=self.game.window.scaled_height(), tw=16, th=16, color=0x666666)
    glColor4f(1.0, 1.0, 1.0, 1.0)

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    for button in self.buttons:
      hovered = mouse_pos[0] > button[0][0] and mouse_pos[0] <= button[0][0] + button[1][0] and mouse_pos[1] > button[0][1] and mouse_pos[1] <= button[0][1] + button[1][1]
      game.draw_texture_nineslice("gui.png", button[0], button[1], (20 if hovered else 0, 22), (20, 20), (4, 4, 4, 4), 256, 64)
      game.font.draw_text(button[2], button[0][0] + button[1][0] / 2, button[0][1] + 6, 0xFFFFFF, 0.5)

class MainMenu(Menu):
  SPLASHES = ["BRESENHAM!", "FINITE VOXELS", "DON'T LOOK UP!"]

  def __init__(self, game: Game) -> None:
    super().__init__(game)

  def init_gui(self):
    self.splash = random.choice(MainMenu.SPLASHES)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), (200, 20), "PLAY GAME", self.__play)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), (200, 20), "SETTINGS", self.__settings)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), (200, 20), "QUIT", self.game.shutdown)

  def __play(self):
    self.game.start_world()

  def __settings(self):
    self.game.menu = SettingsMenu(self.game, self)

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    self.render_dirt_bg()
    super().render(game, mouse_pos)
    game.font.draw_text("VOXELS", 1, 1, 0xFFFFFF, 0)
    game.font.draw_text(self.splash, game.window.scaled_width() / 2, 20, 0xFFFF00, 0.5)

class LoadingTerrainMenu(Menu):
  def __init__(self, game: Game) -> None:
    super().__init__(game)
    self.started = False

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    self.render_dirt_bg()
    super().render(game, mouse_pos)
    game.font.draw_text("GENERATING TERRAIN...", self.game.window.scaled_width() / 2, 40, 0xFFFFFF, 0.5)

    if self.started:
      self.game.world = World(self.game)
      self.game.grab_mouse()
      self.game.menu = None

    if not self.started:
      self.started = True

class SettingsMenu(Menu):
  def __init__(self, game: Game, parent: Menu) -> None:
    super().__init__(game)
    self.parent_menu = parent
  
  def init_gui(self):
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 48), (200, 20), f"FOG DISTANCE: {self.__fog_distance_stringify(self.game.fog_distance)}", self.__change_fog)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), (200, 20), f"SHOW BLOCK PREVIEW: {'ON' if self.game.show_block_preview else 'OFF'}", self.__change_block_preview)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), (200, 20), f"V-SYNC: {'ON' if self.game.window.vsync else 'OFF'}", self.__change_vsync)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), (200, 20), f"SOUND: {'ON' if self.game.sound_enabled else 'OFF'}", self.__change_sound)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 58), (200, 20), "DONE", self.__back)

  def __back(self):
    self.game.menu = self.parent_menu
    self.game.save_settings()

  def __change_fog(self):
    self.game.fog_distance += 1
    if self.game.fog_distance > 3:
      self.game.fog_distance = 1

    self.buttons[0][2] = f"FOG DISTANCE: {self.__fog_distance_stringify(self.game.fog_distance)}"

  def __change_block_preview(self):
    self.game.show_block_preview = not self.game.show_block_preview
    self.buttons[1][2] = f"SHOW BLOCK PREVIEW: {'ON' if self.game.show_block_preview else 'OFF'}"

  def __change_vsync(self):
    self.game.window.vsync = not self.game.window.vsync
    self.buttons[2][2] = f"V-SYNC: {'ON' if self.game.window.vsync else 'OFF'}"
  
  def __change_sound(self):
    self.game.sound_enabled = not self.game.sound_enabled
    self.buttons[3][2] = f"SOUND: {'ON' if self.game.sound_enabled else 'OFF'}"

  def __fog_distance_stringify(self, distance: int):
    if distance == 3:
      return "FAR"
    if distance == 2:
      return "NORMAL"
    if distance == 1:
      return "CLOSEST"
    return "INVALID"

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    if game.world == None:
      self.render_dirt_bg()
    else:
      game.draw_rect((0, 0), (game.window.scaled_width(), self.game.window.scaled_height()), 0x90000000)
    game.font.draw_text("SETTINGS", game.window.scaled_width() / 2, 20, 0xFFFFFF, 0.5)
    super().render(game, mouse_pos)

class PauseMenu(Menu):
  def init_gui(self):
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), (200, 20), "CONTINUE GAME", self.__play)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), (200, 20), "SETTINGS", self.__settings)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), (200, 20), "RETURN TO TITLE", self.__return_main)

  def __play(self):
    self.game.menu = None
    self.game.grab_mouse()

  def __settings(self):
    self.game.menu = SettingsMenu(self.game, self)

  def __return_main(self):
    self.game.menu = MainMenu(self.game)
    self.game.world = None
    self.game.player = None
    self.game.show_debug = False

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    game.draw_rect((0, 0), (game.window.scaled_width(), self.game.window.scaled_height()), 0x90000000)
    game.font.draw_text("GAME MENU", game.window.scaled_width() / 2, 40, 0xFFFFFF, 0.5)
    super().render(game, mouse_pos)

class Font:
  CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.!:/-'"

  def __init__(self, game: Game):
    self.game = game

  def draw_text(self, message: str, x: int, y: int, color: int, align: float, shadow=True):
    if shadow:
      self.__draw_text(message, x + 1, y + 1, 0x000000, align)
    self.__draw_text(message, x, y, color, align)

  def __draw_text(self, message: str, x: int, y: int, color: int, align: float):
    glColor4f((color >> 16 & 0xFF) / 255.0, (color >> 8 & 0xFF) / 255.0, (color & 0xFF) / 255.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    self.game.texture_manager.get("gui.png").bind()

    glBegin(GL_QUADS)

    xx = x - (len(message) * 8) * align

    for char in message:
      if char == ' ':
        xx += 8
        continue
      
      idx = Font.CHARS.find(char)
      u = (idx % 21) * 8
      v = 48 + (idx // 21) * 8

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

class Game:
  def __init__(self):
    self.show_debug = False
    self.window = GameWindow(700, 450)
    self.texture_manager = TextureManager()
    self.current_fps = 0
    self.mouse = {
      'x': 0,
      'y': 0,
      'dx': 0,
      'dy': 0
    }
    self.running = True
    self.player: Player | None = None 
    self.menu: Menu | None = None
    self.window.mouse_button_func(self.on_mouse_button)
    self.window.scroll_func(self.on_scroll)
    self.window.size_changed_func(self.on_framebuffer_size_changed)
    self.window.cursor_pos_func(self.on_cursor_pos)
    self.window.key_func(self.on_key)
    self.world: World | None = None
    self.hit_result: HitResult | None = None
    self.font = Font(self)
    self.selected_tile = 1
    self.fog_distance = 1
    self.show_block_preview = True
    self.sound_enabled = True
    self.chunk_updates = 0
    self.workaround_hit_face = 0
    self.click_sound = pygame.mixer.Sound("click.mp3")
    self.block_sound = pygame.mixer.Sound("block.mp3")
    self.block_sound.set_volume(0.7)

  def load_settings(self):
    try:
      with open("settings.txt", "r") as f:
        for line in f.readlines():
          ln = line.strip()
          option_ln = ln.split(":")

          if len(option_ln) < 2:
            continue

          if option_ln[0] == "fog_distance" and option_ln[1].isnumeric():
            self.fog_distance = int(option_ln[1])

          if option_ln[0] == "show_block_preview":
            self.show_block_preview = option_ln[1] == "True"

          if option_ln[0] == "vsync":
            self.window.vsync = option_ln[1] == "True"
          
          if option_ln[0] == "sound":
            self.sound_enabled = option_ln[1] == "True"
    except Exception:
      pass

  def save_settings(self):
    with open("settings.txt", "w") as f:
      f.write(f"vsync:{self.window.vsync}\n")
      f.write(f"fog_distance:{self.fog_distance}\n")
      f.write(f"show_block_preview:{self.show_block_preview}\n")
      f.write(f"sound:{self.sound_enabled}")

  def play_sound(self, sound: pygame.mixer.Sound):
    if self.sound_enabled:
      pygame.mixer.Sound.play(sound)

  def start_world(self):
    self.menu = LoadingTerrainMenu(self)

  def shutdown(self):
    self.running = False

  def on_scroll(self, x_offset, y_offset):
    step = 1 if y_offset > 0 else -1

    self.selected_tile -= step

    if self.selected_tile < 1:
      self.selected_tile = 9

    if self.selected_tile > 9:
      self.selected_tile = 1

  def on_framebuffer_size_changed(self):
    glViewport(0, 0, self.window.width, self.window.height)
    if self.menu != None:
      self.menu.resize()

  def on_mouse_button(self, button: int, action: int):
    if action == glfw.PRESS and button == 0 and self.menu != None:
      self.menu.mouse_clicked((self.mouse['x'] / self.window.scale_factor, self.mouse['y'] / self.window.scale_factor))

    if action == glfw.PRESS and button == 0 and self.menu == None and self.hit_result != None:
      self.world.set_tile(self.hit_result.bx, self.hit_result.by, self.hit_result.bz, 0)
      self.play_sound(self.block_sound)
    
    if action == glfw.PRESS and button == 1 and self.menu == None and self.hit_result != None:
      self.world.set_tile(self.hit_result.bx, self.hit_result.by + 1, self.hit_result.bz, self.selected_tile)
      self.play_sound(self.block_sound)
  
  def on_cursor_pos(self, xpos, ypos):
    self.mouse['dx'] = xpos - self.mouse['x']
    self.mouse['dy'] = self.mouse['y'] - ypos
    self.mouse['x'] = xpos
    self.mouse['y'] = ypos

  def on_key(self, key, scancode, action):
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE and self.menu == None:
      self.menu = PauseMenu(self)
      self.ungrab_mouse()

    if action == glfw.PRESS and key == glfw.KEY_F7:
      self.texture_manager.reload_textures()

    if action == glfw.PRESS and key == glfw.KEY_F and self.menu == None:
      self.fog_distance += 1
      if self.fog_distance > 3:
        self.fog_distance = 1

    if action == glfw.PRESS and key == glfw.KEY_F3:
      self.show_debug = not self.show_debug

    if action == glfw.PRESS and self.menu == None and key == glfw.KEY_N:
      self.workaround_hit_face += 1
      if self.workaround_hit_face > 5:
        self.workaround_hit_face = 0

    if action == glfw.PRESS and (key >= glfw.KEY_1 and key <= glfw.KEY_9):
      self.selected_tile = key - glfw.KEY_0

  def grab_mouse(self):
    glfw.set_cursor_pos(self.window.handle, self.window.width / 2, self.window.height / 2)
    glfw.set_input_mode(self.window.handle, glfw.CURSOR, glfw.CURSOR_DISABLED)

  def ungrab_mouse(self):
    glfw.set_input_mode(self.window.handle, glfw.CURSOR, glfw.CURSOR_NORMAL)
    glfw.set_cursor_pos(self.window.handle, self.window.width / 2, self.window.height / 2)

  def get_camera_pos(self):
    return [self.player.x, self.player.y, self.player.z]

  def run(self):
    self.window.init("Voxels")
    self.load_settings()
    self.texture_manager.load('grass.png')
    self.texture_manager.load('gui.png')
    self.texture_manager.load('bg.png')
    self.texture_manager.load('prof.png')
    self.texture_manager.load('not_bedrock.png')
    self.menu = MainMenu(self)

    glClearColor(0.239, 0.686, 0.807, 1.0)
    last_time = glfw.get_time()
    frame_counter = 0
    tick_last_time = glfw.get_time()
    tick_delta = 0

    while self.running:
      if self.window.should_close():
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
      
      self.window.update_frame()

      frame_counter += 1

      now = glfw.get_time()
      if now - last_time > 1.0:
        last_time = now
        self.current_fps = frame_counter
        frame_counter = 0

    self.save_settings()
    if self.world != None:
      self.world.dispose()
    self.texture_manager.dispose()
    glfw.terminate()

  def render(self, tick_delta: float):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, self.window.width / self.window.height, 0.05, 1000.0)
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

      # idek
      start_pos = self.get_camera_pos()
      end_pos = self.get_camera_pos()
      rv0 = math.cos(-self.player.rot_y * (math.pi / 180.0) - math.pi)
      rv1 = math.sin(-self.player.rot_y * (math.pi / 180.0) - math.pi)
      rv2 = -math.cos(-self.player.rot_x * math.pi / 180.0)
      rv3 =-math.sin(-self.player.rot_x * math.pi / 180.0)

      end_pos[0] -= rv1 * rv2 * 7
      end_pos[1] -= rv3 * 7
      end_pos[2] -= rv0 * rv2 * 7
      #

      self.hit_result = bresenham(self.world, start_pos, end_pos, lambda tile_id : TILE_TYPES[tile_id])

      self.texture_manager.get("grass.png").bind()
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

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, self.window.scaled_width(), self.window.scaled_height(), 0, 1000.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -2000.0)

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ONE_MINUS_SRC_COLOR)
    self.draw_texture("gui.png", self.window.scaled_width() / 2 - 8, self.window.scaled_height() / 2 - 8, 16, 16, 240, 0, 16, 16, 256, 64)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    self.draw_texture("gui.png", self.window.scaled_width() / 2 - 91, self.window.scaled_height() - 22, 182, 22, 0, 0, 182, 22, 256, 64)
    
    self.texture_manager.get("grass.png").bind()
    
    if self.show_block_preview:
      glEnable(GL_CULL_FACE)
      glPushMatrix()
      glTranslatef(self.window.scaled_width() - 45, 80, 20)
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
      self.draw_texture("grass.png", self.window.scaled_width() / 2 - 91 + 3 + i * 20, self.window.scaled_height() - 22 + 3, 16, 16, (tile_txr % 3) * 16, (tile_txr // 3) * 16, 16, 16, 48, 64)

    self.draw_texture("gui.png", self.window.scaled_width() / 2 - 91 + (self.selected_tile - 1) * 20, self.window.scaled_height() - 22 - 1, 24, 24, 40, 22, 24, 24, 256, 64)

    glDisable(GL_BLEND)

    if self.world != None:
      self.font.draw_text("VOXELS", 1, 1, 0xFFFFFF, 0)

      if self.show_debug:
        self.font.draw_text(f"{self.current_fps} FPS", 1, 11, 0xFFFFFF, 0)
        self.font.draw_text(f"{'X: {:.4f}'.format(self.player.x)}", 1, 21, 0xFFFFFF, 0)
        self.font.draw_text(f"{'Y: {:.4f}'.format(self.player.y)}", 1, 31, 0xFFFFFF, 0)
        self.font.draw_text(f"{'Z: {:.4f}'.format(self.player.z)}", 1, 41, 0xFFFFFF, 0)
        self.font.draw_text(f"SELECTED TILE: {self.selected_tile}", 1, 51, 0xFFFFFF, 0)
        self.font.draw_text("PRESS F3 TO SHOW/HIDE DEBUG", 1, 71, 0xFFFFFF, 0)
        self.font.draw_text("PRESS 1-9 TO SELECT BLOCKS", 1, 81, 0xFFFFFF, 0)
        self.font.draw_text("PRESS F7 TO RELOAD TEXTURES", 1, 91, 0xFFFFFF, 0)
        self.font.draw_text(f"PYTHON {platform.sys.version_info.major}.{platform.sys.version_info.minor}.{platform.sys.version_info.micro}", self.window.scaled_width() - 1, 1, 0xFFFFFF, 1)
        self.font.draw_text(f"DISPLAY: {self.window.width}X{self.window.height}", self.window.scaled_width() - 1, 21, 0xFFFFFF, 1)
      else:
        self.font.draw_text("PRESS F3 TO SHOW DEBUG", 1, 11, 0xFFFFFF, 0)
        self.font.draw_text("PRESS 1-9 TO SELECT BLOCKS", 1, 21, 0xFFFFFF, 0)

    if self.menu != None:
      self.menu.render(self, (self.mouse['x'] / self.window.scale_factor, self.mouse['y'] / self.window.scale_factor))

  def draw_texture_nineslice(self, texture_name, pos: tuple[int, int], size: tuple[int, int], uv: tuple[int, int], uv_size: tuple[int, int], nineslice: tuple[int, int, int, int], tw: int, th: int):
    self.texture_manager.get(texture_name).bind()
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
    self.texture_manager.get(texture_name).bind()

    glColor4f((color >> 16 & 0xFF) / 255.0, (color >> 8 & 0xFF) / 255.0, (color & 0xFF) / 255.0, 1.0)
    glBegin(GL_QUADS)
    self.__draw_texture_quad(x, y, width, height, u, v, us, vs, tw, th)
    glEnd()

  def tick(self):
    if self.world != None:
      self.world.tick()
      self.player.tick()

if __name__ == "__main__":
  pygame.init()
  game = Game()
  game.run()
  pygame.quit()