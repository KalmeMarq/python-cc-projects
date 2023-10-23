from __future__ import annotations
import glfw
from typing import Dict
from OpenGL.GL import *
import PIL.Image as Image
import math
from utils import perspective
import numpy as np
import random
from enum import Enum

class TextureManager:
  def __init__(self):
    self.textures: Dict[str, np.uintc] = {}

  def load(self, path: str) -> None:
    im = Image.open(path);
    imdata = np.frombuffer(im.tobytes(), np.uint8)

    txr_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, txr_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, im.width, im.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imdata)
    glBindTexture(GL_TEXTURE_2D, 0)
    self.textures[path] = txr_id

  def get(self, path: str) -> np.uintc:
    return self.textures[path]
    
  def dispose(self) -> None:
    for txr_id in self.textures.values():
      glDeleteTextures([txr_id])

class Player:
  def __init__(self):
    self.x = 0
    self.y = 17
    self.z = 0
    self.old_x = 0
    self.old_y = 0
    self.old_z = 0
    self.rot_x = 0
    self.rot_y = 0

  def turn(self, xr, yr):
    self.rot_y = self.rot_y + xr * 0.15
    self.rot_x = self.rot_x - yr * 0.15

    if self.rot_x < -90.0:
      self.rot_x = -90.0

    if self.rot_x > 90.0:
      self.rot_x = 90.

TILE_TYPES: Dict[int, TileType] = {}

class TileType:
  def __init__(self, down_txr: int, up_txr: int, north_txr: int, south_txr: int, west_txr: int, east_txr: int) -> None:
    self.down_txr = down_txr
    self.up_txr = up_txr
    self.north_txr = north_txr
    self.south_txr = south_txr
    self.west_txr = west_txr
    self.east_txr = east_txr


TILE_TYPES[1] = TileType(1, 3, 0, 0, 0, 0)
TILE_TYPES[2] = TileType(1, 1, 1, 1, 1, 1)
TILE_TYPES[3] = TileType(4, 4, 4, 4, 4, 4)
TILE_TYPES[4] = TileType(2, 2, 5, 5, 5, 5)
TILE_TYPES[5] = TileType(6, 6, 6, 6, 6, 6)
TILE_TYPES[6] = TileType(7, 7, 7, 7, 7, 7)
TILE_TYPES[7] = TileType(8, 8, 8, 8, 8, 8)

CHUNK_HEIGHT = 32

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

class Chunk:
  def __init__(self, x: int, z: int):
    self.x = x
    self.z = z
    self.blocks = np.zeros(16 * 16 * CHUNK_HEIGHT, dtype=np.uint8)
    self.list = glGenLists(2)
    self.generate()

  def generate(self):
    for x in range(16):
      for y in range(CHUNK_HEIGHT):
        for z in range(16):
          if y == 0:
            self.blocks[(y * 16 + z) * 16 + x] = 3
          elif y < 15:
            self.blocks[(y * 16 + z) * 16 + x] = 2
          elif y == 15:
            self.blocks[(y * 16 + z) * 16 + x] = 1
          else:
            vl = random.randrange(0, 300)
            if vl < 2:
              self.blocks[(y * 16 + z) * 16 + x] = random.randrange(4, 8)

  def set_tile(self, x: int, y: int, z: int, tile_id: int):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return
    self.blocks[(y * 16 + z) * 16 + x] = tile_id

  def get_tile(self, x: int, y: int, z: int):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return 0
    return self.blocks[(y * 16 + z) * 16 + x]

  def rebuild_geometry(self, layer: RenderLayer, world: World, texture_manager: TextureManager):
    glNewList(self.list + layer.value, GL_COMPILE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_manager.get("grass.png"))

    glBegin(GL_QUADS)

    for y in range(CHUNK_HEIGHT):
      for x in range(16):
        for z in range(16):
          bx = x + self.x * 16
          by = y
          bz = z + self.z * 16

          tile = world.get_tile(x, y, z)
          if tile < 1 or tile == 7 and layer == RenderLayers['SOLID']:
            continue

          tile_type = TILE_TYPES[tile]

          x0 = bx
          y0 = by
          z0 = bz
          x1 = bx + 1.0
          y1 = by + 1.0
          z1 = bz + 1.0

          if world.get_tile(bx, by - 1, bz) == 0:
            u = (tile_type.down_txr % 3) * 16
            v = tile_type.down_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 48.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 48.0

            glColor4f(0.6, 0.6, 0.6, 1.0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y0, z1)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y0, z0)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y0, z0)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y0, z1)

          if world.get_tile(bx, by + 1, bz) == 0:
            u = (tile_type.up_txr % 3) * 16
            v = tile_type.up_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 48.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 48.0

            glColor4f(1.0, 1.0, 1.0, 1.0)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y1, z1)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y1, z0)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y1, z0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y1, z1) 

          if world.get_tile(bx, by, bz - 1) == 0:
            u = (tile_type.north_txr % 3) * 16
            v = tile_type.north_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 48.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 48.0
            
            glColor4f(0.6, 0.6, 0.6, 1.0)
            glTexCoord2f(u1, v0)
            glVertex3f(x0, y1, z0)
            glTexCoord2f(u0, v0)
            glVertex3f(x1, y1, z0)
            glTexCoord2f(u0, v1)
            glVertex3f(x1, y0, z0)
            glTexCoord2f(u1, v1)
            glVertex3f(x0, y0, z0)

          if world.get_tile(bx, by, bz + 1) == 0:
            u = (tile_type.south_txr % 3) * 16
            v = tile_type.south_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 48.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 48.0

            glColor4f(0.6, 0.6, 0.6, 1.0)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y1, z1)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y0, z1)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y0, z1)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y1, z1)

          if world.get_tile(bx - 1, by, bz) == 0:
            u = (tile_type.west_txr % 3) * 16
            v = tile_type.west_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 48.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 48.0

            glColor4f(0.8, 0.8, 0.8, 1.0)
            glTexCoord2f(u1, v0)
            glVertex3f(x0, y1, z1)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y1, z0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y0, z0)
            glTexCoord2f(u1, v1)
            glVertex3f(x0, y0, z1)

          if world.get_tile(bx + 1, by, bz) == 0:
            u = (tile_type.east_txr % 3) * 16
            v = tile_type.east_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 48.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 48.0

            glColor4f(0.8, 0.8, 0.8, 1.0)
            glTexCoord2f(u0, v1)
            glVertex3f(x1, y0, z1)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y0, z0)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y1, z0)
            glTexCoord2f(u0, v0)
            glVertex3f(x1, y1, z1)
          
    glEnd()
    glEndList()

  def render(self, layer: RenderLayer):
    glCallList(self.list + layer.value)

  def dispose(self):
    glDeleteLists(self.list, 2)

class World:
  def __init__(self, game: Game):
    self.x_chunks = 4
    self.z_chunks = 4
    self.chunks: list[Chunk] = []
    for x in range(0, self.x_chunks):
      for z in range(0, self.z_chunks):
        self.chunks.append(Chunk(x, z))

    for chunk in self.chunks:
      chunk.rebuild_geometry(RenderLayers['SOLID'], self, game.texture_manager)
      chunk.rebuild_geometry(RenderLayers['TRANSLUCENT'], self, game.texture_manager)

  def set_tile(self, x: int, y: int, z: int, tile_id: int):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return
    self.chunks[cz * 2 + cx].set_tile(x % 16, y % 16, z % 16, tile_id)

  def get_tile(self, x: int, y: int, z: int):
    cx = x // 16
    cz = z // 16
    if cx < 0 or cx >= self.x_chunks or cz < 0 or cz >= self.z_chunks or y < 0 or y >= CHUNK_HEIGHT:
      return 0
    return self.chunks[cz * 2 + cx].get_tile(x % 16, y % CHUNK_HEIGHT, z % 16)

  def render(self):
    RenderLayers['SOLID'].begin()

    for chunk in self.chunks:
      chunk.render(layer=RenderLayers['SOLID'])
    
    RenderLayers['SOLID'].end()

    RenderLayers['TRANSLUCENT'].begin()
    for chunk in self.chunks:
      chunk.render(layer=RenderLayers['TRANSLUCENT'])
    glDisable(GL_BLEND)
    
    RenderLayers['TRANSLUCENT'].end()

  def dispose(self):
    for chunk in self.chunks:
      chunk.dispose()

class Game:
  def __init__(self):
    if not glfw.init():
      exit(0)

    self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.!:/"

    self.width = 800
    self.height = 600

    glfw.default_window_hints()
    self.window = glfw.create_window(self.width, self.height, "Voxels", None, None)
    imicon = Image.open("icon.png")
    glfw.set_window_icon(self.window, 1, [imicon])
    glfw.make_context_current(self.window)
    glfw.swap_interval(1)

    self.texture_manager = TextureManager()
    self.texture_manager.load('grass.png')
    self.texture_manager.load('gui.png')
    self.current_fps = 0
    self.mouse = {
      'x': 0,
      'y': 0,
      'dx': 0,
      'dy': 0
    }

    self.running = True
    self.player = Player()
    glfw.set_key_callback(self.window, lambda _,key,scancode,action,mods : self.on_key(key, scancode, action, mods))
    glfw.set_cursor_pos_callback(self.window, lambda _,xpos,ypos : self.on_cursor_pos(xpos, ypos))
    glfw.set_mouse_button_callback(self.window, lambda _,button,action,mods : self.on_mouse_button(button, action, mods))
    glfw.set_framebuffer_size_callback(self.window, lambda _,w,h : self.on_framebuffer_size_changed(w, h))

    self.world = World(self)

  def on_framebuffer_size_changed(self, width, height):
    self.width = width
    self.height = height
    glViewport(0, 0, self.width, self.height)
    self.proj_mat = perspective(1.22172, self.width / self.height, 0.05, 1000.0)

  def on_mouse_button(self, button, action, mods):
    pass

  def on_cursor_pos(self, xpos, ypos):
    self.mouse['dx'] = xpos - self.mouse['x']
    self.mouse['dy'] = self.mouse['y'] - ypos
    self.mouse['x'] = xpos
    self.mouse['y'] = ypos

  def on_key(self, key, scancode, action, mods):
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE:
      self.running = False

  def run(self):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    last_time = glfw.get_time()
    frame_counter = 0
    self.proj_mat = perspective(1.22172, self.width / self.height, 0.05, 1000.0)
    tick_last_time = glfw.get_time()
    tick_delta = 0
    glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

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

      self.player.turn(self.mouse['dx'], self.mouse['dy'])
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

    self.world.dispose()
    self.texture_manager.dispose()
    glfw.terminate()

  def render(self, tick_delta: float):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glLoadMatrixf(self.proj_mat)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(self.player.rot_x, 1.0, 0.0, 0.0);
    glRotatef(self.player.rot_y, 0.0, 1.0, 0.0);
    glTranslatef(-self.player.x, -self.player.y, -self.player.z)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get("grass.png"))  
    self.world.render()
  
    glClear(GL_DEPTH_BUFFER_BIT)

    scaled_width = self.width / 2
    scaled_height = self.height / 2

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, scaled_width, scaled_height, 0, 1000.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -2000.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ONE_MINUS_SRC_COLOR)
    self.draw_texture("gui.png", scaled_width / 2 - 8, scaled_height / 2 - 8, 16, 16, 240, 0, 16, 16, 256, 64)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    self.draw_texture("gui.png", scaled_width / 2 - 91, scaled_height - 22, 182, 22, 0, 0, 182, 22, 256, 64)
    glDisable(GL_BLEND)

    self.draw_text("VOXELS ALPHA", 1, 1, 0xFFFFFF, 0)
    self.draw_text(f"{self.current_fps} FPS", 1, 11, 0xFFFFFF, 0)
    self.draw_text(f"{'XYZ: {:.4f} / {:.4f} / {:.4f}'.format(self.player.x, self.player.y, self.player.z)}", 1, 21, 0xFFFFFF, 0)
    self.draw_text(f"PYTHON {platform.sys.version_info.major}.{platform.sys.version_info.minor}.{platform.sys.version_info.micro}", scaled_width - 1, 1, 0xFFFFFF, 1)
    self.draw_text(f"DISPLAY: {self.width}X{self.height}", scaled_width - 1, 11, 0xFFFFFF, 1)

  def draw_texture(self, texture_name, x: int, y: int, width: int, height: int, u: int, v: int, us: int, vs: int, tw: int, th: int):
    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get(texture_name))

    u0 = u / tw
    v0 = v / th
    u1 = (u + us) / tw
    v1 = (v + vs) / th

    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(u0, v0)
    glVertex3f(x, y, 0)
    glTexCoord2f(u0, v1)
    glVertex3f(x, y + height, 0)
    glTexCoord2f(u1, v1)
    glVertex3f(x + width, y + height, 0)
    glTexCoord2f(u1, v0)
    glVertex3f(x + width, y, 0)
    glEnd()

  def draw_text(self, message: str, x: int, y: int, color: int, align: float):
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
    xa = 0
    ya = 0
    za = 0

    if glfw.get_key(self.window, glfw.KEY_W) != glfw.RELEASE:
      za -= 1
    
    if glfw.get_key(self.window, glfw.KEY_S) != glfw.RELEASE:
      za += 1

    if glfw.get_key(self.window, glfw.KEY_A) != glfw.RELEASE:
      xa -= 1
    
    if glfw.get_key(self.window, glfw.KEY_D) != glfw.RELEASE:
      xa += 1

    if glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) != glfw.RELEASE or glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) != glfw.RELEASE:
      ya -= 1
    
    if glfw.get_key(self.window, glfw.KEY_SPACE) != glfw.RELEASE:
      ya += 1

    psin = math.sin(self.player.rot_y * math.pi / 180.0);
    pcos = math.cos(self.player.rot_y * math.pi / 180.0);

    self.player.x += xa * pcos - za * psin
    self.player.y += ya
    self.player.z += za * pcos + xa * psin

if __name__ == "__main__":
  game = Game()
  game.run()