from __future__ import annotations
import glfw
from typing import Dict
from OpenGL.GL import *
import PIL.Image as Image
import math
import utils
import numpy as np
import random
from enum import Enum

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

class Player:
  def __init__(self):
    self.x = 16
    self.y = 64
    self.z = 16
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
TILE_TYPES[8] = TileType(11, 11, 11, 11, 11, 11)

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

  def flush(self):
    if self.__vertices > 0:
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
    self.blocks = np.zeros(16 * 16 * CHUNK_HEIGHT, dtype=np.uint8)
    self.list = glGenLists(2)
    self.generate()
    self.__dirty = True

  def generate(self):
    for x in range(16):
      for y in range(CHUNK_HEIGHT):
        for z in range(16):
          if y > 32:
            continue
          elif y == 0:
            self.blocks[(y * 16 + z) * 16 + x] = 3
          elif y < 15:
            self.blocks[(y * 16 + z) * 16 + x] = 2
          elif y == 15:
            self.blocks[(y * 16 + z) * 16 + x] = 1
          else:
            vl = random.randrange(0, 300)
            if vl < 2:
              self.blocks[(y * 16 + z) * 16 + x] = random.randrange(4, 9)


      if self.x == 0 and self.z == 0:
        self.set_tile(2, 16, 2, 4)
        self.set_tile(2, 17, 2, 4)
        self.set_tile(2, 18, 2, 4)
        self.set_tile(2, 19, 2, 4)

        for tx in range(0, 5):
          for tz in range(0, 5):
            self.set_tile(tx, 20, tz, 8)

        for tx in range(1, 4):
          for tz in range(1, 4):
            self.set_tile(tx, 21, tz, 8)

  def set_tile(self, x: int, y: int, z: int, tile_id: int):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return
    self.blocks[(y * 16 + z) * 16 + x] = tile_id
    self.__dirty = True
    print(f"Chunk[{self.x}/{self.z}] is dirty")

  def get_tile(self, x: int, y: int, z: int):
    if x < 0 or x >= 16 or y < 0 or y >= CHUNK_HEIGHT or z < 0 or z >= 16:
      return 0
    return self.blocks[(y * 16 + z) * 16 + x]

  def rebuild_geometry(self, layer: RenderLayer, world: World, texture_manager: TextureManager, vertex_drawer = VertexDrawer()):
    glNewList(self.list + layer.value, GL_COMPILE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_manager.get("grass.png"))

    vertex_drawer.begin(GL_QUADS)

    for y in range(CHUNK_HEIGHT):
      for x in range(16):
        for z in range(16):
          bx = x + self.x * 16
          by = y
          bz = z + self.z * 16

          tile = world.get_tile(bx, by, bz)
          if tile < 1 or (tile == 7 or tile == 8) and layer == RenderLayers['SOLID']:
            continue

          tile_type = TILE_TYPES[tile]

          x0 = bx
          y0 = by
          z0 = bz
          x1 = bx + 1.0
          y1 = by + 1.0
          z1 = bz + 1.0

          if tile == 8 or world.get_tile(bx, by - 1, bz) == 0:
            u = (tile_type.down_txr % 3) * 16
            v = tile_type.down_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
            vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
            vertex_drawer.vertex_uv(x0, y0, z0, u0, v0)
            vertex_drawer.vertex_uv(x1, y0, z0, u1, v0)
            vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)

          if tile == 8 or world.get_tile(bx, by + 1, bz) == 0:
            u = (tile_type.up_txr % 3) * 16
            v = tile_type.up_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(1.0, 1.0, 1.0, 1.0)
            vertex_drawer.vertex_uv(x1, y1, z1, u1, v1)
            vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
            vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
            vertex_drawer.vertex_uv(x0, y1, z1, u0, v1)

          if tile == 8 or world.get_tile(bx, by, bz - 1) == 0:
            u = (tile_type.north_txr % 3) * 16
            v = tile_type.north_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0
            
            vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
            vertex_drawer.vertex_uv(x0, y1, z0, u1, v0)
            vertex_drawer.vertex_uv(x1, y1, z0, u0, v0)
            vertex_drawer.vertex_uv(x1, y0, z0, u0, v1)
            vertex_drawer.vertex_uv(x0, y0, z0, u1, v1)

          if tile == 8 or world.get_tile(bx, by, bz + 1) == 0:
            u = (tile_type.south_txr % 3) * 16
            v = tile_type.south_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
            vertex_drawer.vertex_uv(x0, y1, z1, u0, v0)
            vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
            vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)
            vertex_drawer.vertex_uv(x1, y1, z1, u1, v0)

          if tile == 8 or world.get_tile(bx - 1, by, bz) == 0:
            u = (tile_type.west_txr % 3) * 16
            v = tile_type.west_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
            vertex_drawer.vertex_uv(x0, y1, z1, u1, v0)
            vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
            vertex_drawer.vertex_uv(x0, y0, z0, u0, v1)
            vertex_drawer.vertex_uv(x0, y0, z1, u1, v1)

          if tile == 8 or world.get_tile(bx + 1, by, bz) == 0:
            u = (tile_type.east_txr % 3) * 16
            v = tile_type.east_txr // 3 * 16

            u0 = u / 48.0
            v0 = v / 64.0
            u1 = (u + 16) / 48.0
            v1 = (v + 16) / 64.0

            vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
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

    vertex_drawer.flush()

  def render(self, layer: RenderLayer, texture_manager: TextureManager):
    if self.__dirty:
      print(f"Chunk[{self.x}/{self.z}] is clean")
      self.rebuild_geometry(RenderLayers['SOLID'], self.world, texture_manager)
      self.rebuild_geometry(RenderLayers['TRANSLUCENT'], self.world, texture_manager)
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
    for x in range(0, self.x_chunks):
      for z in range(0, self.z_chunks):
        self.chunks.append(Chunk(self, x, z))

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
    return self.chunks[cz * 2 + cx].get_tile(x % 16, y, z % 16)

  def render(self):
    RenderLayers['SOLID'].begin()

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

    RenderLayers['TRANSLUCENT'].end()

  def dispose(self):
    for chunk in self.chunks:
      chunk.dispose()

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
    self.game.menu = None
    self.game.grab_mouse()

  def render(self, game: Game, mouse_pos: tuple[int, int]):
    game.draw_texture(texture_name="bg.png", x=0, y=0, width=game.width / 2, height=game.height / 2, u=0, v=0, us=game.width / 2, vs=game.height / 2, tw=16, th=16, color=0x666666)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    super().render(game, mouse_pos)
    game.draw_text("VOXELS", 1, 1, 0xFFFFFF, 0)

class PauseMenu(Menu):
  def init_gui(self):
    self.add_button((self.game.width / 4 - 100, self.game.height / 4 - 48), (200, 20), "RETURN TO GAME", self.__play)
    self.add_button((self.game.width / 4 - 100, self.game.height / 4 - 24), (200, 20), "QUIT", self.__return_main)

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

  def raycast(origin: tuple[float, float, float], direction: tuple[int, int, int], radius: int = 7):
    # A Fast Voxel Traversal Algorithm for Ray Tracing

    x = math.floor(origin[0])
    y = math.floor(origin[1])
    z = math.floor(origin[2])

    dx = direction[0]
    dy = direction[1]
    dz = direction[2]

    step_x = utils.signum(dx)
    step_y = utils.signum(dy)
    step_z = utils.signum(dz)

    tmax_x = utils.intbound(origin[0], dx)
    tmax_y = utils.intbound(origin[1], dy)
    tmax_z = utils.intbound(origin[2], dz)

    tdelta_x = step_x / dx
    tdelta_y = step_y / dy
    tdelta_z = step_z / dz

    face = [0, 0, 0]

    if dx == 0 and dy == 0 and dz == 0:
      raise Exception("Raycast in zero direction!")
    
    radius /= math.sqrt(dx * dx + dy * dy + dz * dz)

    wx = 4 * 16
    wy = CHUNK_HEIGHT
    wz = 4 * 16

    while (x < wx if step_x > 0 else x >= 0) and (y < wy if step_y > 0 else y >= 0) and (z < wz if step_z > 0 else z >= 0):
      pass

      if tmax_x < tmax_y:
        if tmax_x < tmax_z:
          if tmax_x > radius:
            break
        
    return None

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

    if world.get_tile(point[0], point[1], point[2]) != 0:
      return HitResult(point[0], point[1], point[2], world.get_tile(point[0], point[1], point[2]), 0)

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
    self.menu = None # MainMenu(self)
    self.grab_mouse()

    self.world = World(self)
    self.hit_result: HitResult | None = None

  def shutdown(self):
    self.running = False

  def set_icon(self, path: str):
    imicon = Image.open("res/" + path)
    glfw.set_window_icon(self.window, 1, [imicon])

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

  def on_cursor_pos(self, xpos, ypos):
    self.mouse['dx'] = xpos - self.mouse['x']
    self.mouse['dy'] = self.mouse['y'] - ypos
    self.mouse['x'] = xpos
    self.mouse['y'] = ypos

  def on_key(self, key, scancode, action, mods):
    if action == glfw.PRESS and key == glfw.KEY_ESCAPE and self.menu == None:
      self.menu = PauseMenu(self)
      self.ungrab_mouse()

    if action == glfw.PRESS and key == glfw.KEY_F3:
      self.show_debug = not self.show_debug

  def grab_mouse(self):
    glfw.set_cursor_pos(self.window, self.width / 2, self.height / 2)
    glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

  def ungrab_mouse(self):
    glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    glfw.set_cursor_pos(self.window, self.width / 2, self.height / 2)

  def run(self):
    glClearColor(0.239, 0.686, 0.807, 0.0)
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
    glTranslatef(-self.player.x, -self.player.y - 1, -self.player.z)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    look_vec = [
      1 * 7,
      0,
      0
    ]

    self.hit_result = bresenham(self.world, [self.player.x, self.player.y, self.player.z], [self.player.x + look_vec[0], self.player.y + look_vec[1], self.player.z + look_vec[2]])

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
    glDisable(GL_BLEND)

    if self.menu != None:
      self.menu.render(self, (self.mouse['x'] / 2, self.mouse['y'] / 2))

    if not self.show_debug:
      return

    self.draw_text("VOXELS", 1, 1, 0xFFFFFF, 0)
    self.draw_text(f"{self.current_fps} FPS", 1, 11, 0xFFFFFF, 0)
    self.draw_text(f"{'X: {:.4f}'.format(self.player.x)}", 1, 21, 0xFFFFFF, 0)
    self.draw_text(f"{'Y: {:.4f}'.format(self.player.y)}", 1, 31, 0xFFFFFF, 0)
    self.draw_text(f"{'Z: {:.4f}'.format(self.player.z)}", 1, 41, 0xFFFFFF, 0)
    self.draw_text(f"PYTHON {platform.sys.version_info.major}.{platform.sys.version_info.minor}.{platform.sys.version_info.micro}", scaled_width - 1, 1, 0xFFFFFF, 1)
    self.draw_text(f"DISPLAY: {self.width}X{self.height}", scaled_width - 1, 21, 0xFFFFFF, 1)

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

    xa *= 0.61
    za *= 0.61

    psin = math.sin(self.player.rot_y * math.pi / 180.0);
    pcos = math.cos(self.player.rot_y * math.pi / 180.0);

    # if self.world.get_tile(int(self.player.x), int(self.player.y) - 2, int(self.player.z)) == 0:
    #   ya -= 1
    # else:
    #   ya = 0
 
    self.player.x += xa * pcos - za * psin
    self.player.y += ya
    self.player.z += za * pcos + xa * psin


if __name__ == "__main__":
  game = Game()
  game.run()