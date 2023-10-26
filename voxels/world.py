import random
import time
from OpenGL.GL import *
from constants import *
from player import Player
from tiles import BLOCK_TYPES
from render_layers import RenderLayers
from utils import VertexDrawer, AABB
import utils

class Chunk:
  CHUNK_UPDATES = 0

  def __init__(self, world, x: int, z: int):
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
          if tile != 0 and not BLOCK_TYPES[tile].allows_light_through:
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

  def rebuild_geometry(self, layer, world, texture_manager):
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

          tile_type = BLOCK_TYPES[tile]

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

  def rebuild_layers(self, texture_manager):
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
             tile_type = BLOCK_TYPES[tile_id]
             if tile_type.is_tickable:
                BLOCK_TYPES[tile_id].random_tick(self.world, x + self.x * 16, y, z + self.z * 16, tile_id)
                return
             

  def tick(self):
    for _ in range(0, random.randint(0, 2)):
      self.__tick_some_block()

  def render(self, layer, texture_manager):
    if self.__dirty:
      self.rebuild_layers(texture_manager)
      if DEBUG_PRINTS:
        print(f"Chunk[x={self.x},z={self.z}] rendered")
      self.__dirty = False

    glCallList(self.__list + layer.value)

  def dispose(self):
    glDeleteLists(self.__list, 2)

class World:
  def __init__(self, game):
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
      glFogf(GL_FOG_DENSITY, 0.07 if self.game.settings.fog_distance == 1 else 0.04 if self.game.settings.fog_distance == 2 else 0.007)
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