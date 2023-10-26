from __future__ import annotations
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from utils import HitResult, bresenham, VertexDrawer, JSONWithCommentsDecoder
from textures import TextureManager
from tiles import BLOCK_TYPES
from window import GameWindow
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from player import Player
from menus import *
from constants import *
from font import Font
from world import World

class GameSettings:
  def __init__(self):
    self.fog_distance = 1
    self.show_block_preview = True
    self.sound_enabled = True
    self.vsync = True
    self.language = "en_us"

  def load(self):
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
            self.vsync = option_ln[1] == "True"
          
          if option_ln[0] == "sound":
            self.sound_enabled = option_ln[1] == "True"
          
          if option_ln[0] == "language":
            self.language = option_ln[1] if ["en_us", "pt_pt"].count(option_ln[1]) > 0 else "en_us"
    except Exception:
      pass
  
  def save(self):
    with open("settings.txt", "w") as f:
      f.write(f"vsync:{self.vsync}\n")
      f.write(f"fog_distance:{self.fog_distance}\n")
      f.write(f"show_block_preview:{self.show_block_preview}\n")
      f.write(f"sound:{self.sound_enabled}\n")
      f.write(f"language:{self.language}")

class Game:
  def __init__(self):
    self.show_debug = False
    self.window = GameWindow(self, 700, 450)
    self.settings = GameSettings()
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
    self.__menu: Menu | None = None
    self.window.mouse_button_func(self.on_mouse_button)
    self.window.scroll_func(self.on_scroll)
    self.window.size_changed_func(self.on_framebuffer_size_changed)
    self.window.cursor_pos_func(self.on_cursor_pos)
    self.window.key_func(self.on_key)
    self.world: World | None = None
    self.hit_result: HitResult | None = None
    self.font = Font(self)
    self.selected_tile = 1
    self.chunk_updates = 0
    self.workaround_hit_face = 0
    self.click_sound = pygame.mixer.Sound("res/sounds/click.mp3")
    self.block_sound = pygame.mixer.Sound("res/sounds/block.mp3")
    self.block_sound.set_volume(0.7)
    self.translations = {}

  @property
  def menu(self):
    return self.__menu
  
  @menu.setter
  def menu(self, menu):
    if self.__menu != None:
      self.__menu.on_remove()

    self.__menu = menu

    if self.__menu != None:
      self.__menu.on_display()

  def load_translations(self):
    with open(f"res/languages/{self.settings.language}.json", "r", encoding="utf-8") as f:
      self.translations = json.load(f)

  def translate_key(self, key: str, *args: object):
    translation: str = key if self.translations.get(key) == None else self.translations.get(key) 
    try:
      return translation.format(*args)
    except Exception:
      return translation

  def play_sound(self, sound: pygame.mixer.Sound):
    if self.settings.sound_enabled:
      pygame.mixer.Sound.play(sound)

  def start_world(self):
    self.menu = LoadingTerrainMenu(self)

  def load_world(self):
    self.world = World(self)
    self.grab_mouse()
    self.menu = None

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
    if action == glfw.PRESS and self.menu != None:
      self.menu.key_pressed(key)

    if action == glfw.PRESS and key == glfw.KEY_ESCAPE and self.menu == None:
      self.menu = PauseMenu(self)
      self.ungrab_mouse()

    if action == glfw.PRESS and key == glfw.KEY_F7:
      self.texture_manager.reload_textures()

    if action == glfw.PRESS and key == glfw.KEY_F and self.menu == None:
      self.settings.fog_distance += 1
      if self.settings.fog_distance > 3:
        self.settings.fog_distance = 1

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
    self.settings.load()
    self.load_translations()
    self.window.init("Voxels")
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
      if self.menu == None and self.world != None:
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

    self.settings.save()
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

      self.hit_result = bresenham(self.world, start_pos, end_pos, lambda tile_id : BLOCK_TYPES[tile_id])

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
    self.draw_texture("gui.png", self.window.scaled_width() / 2 - 8, self.window.scaled_height() / 2 - 8, 16, 16, 240, 0, 16, 16, 256, 256)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    self.draw_texture("gui.png", self.window.scaled_width() / 2 - 91, self.window.scaled_height() - 22, 182, 22, 0, 0, 182, 22, 256, 256)
    
    self.texture_manager.get("grass.png").bind()
    
    if self.settings.show_block_preview:
      glEnable(GL_CULL_FACE)
      glPushMatrix()
      glTranslatef(self.window.scaled_width() - 45, 80, 20)
      glRotatef(-20, 1, 0, 0)
      glRotatef(44, 0, 1, 0)
      glTranslatef(0, -10, 0)
      glScalef(26, -26, 26)

      tile_type = BLOCK_TYPES[self.selected_tile]
      vertex_drawer = VertexDrawer()
      vertex_drawer.begin(GL_QUADS)
      tile_type.render_in_gui(vertex_drawer=vertex_drawer)
      vertex_drawer.flush()
      glPopMatrix()
      glDisable(GL_CULL_FACE)

    for i in range(0, 9):
      tile_txr = BLOCK_TYPES[i + 1].north_txr
      self.draw_texture("grass.png", self.window.scaled_width() / 2 - 91 + 3 + i * 20, self.window.scaled_height() - 22 + 3, 16, 16, (tile_txr % 16) * 16, (tile_txr // 16) * 16, 16, 16, 256, 256)

    self.draw_texture("gui.png", self.window.scaled_width() / 2 - 91 + (self.selected_tile - 1) * 20, self.window.scaled_height() - 22 - 1, 24, 24, 40, 22, 24, 24, 256, 256)

    glDisable(GL_BLEND)

    if self.world != None:
      self.font.draw_text(GAME_VERSION, 1, 1, 0xFFFFFF, 0)

      if self.show_debug:
        self.font.draw_text(f"{self.current_fps} FPS", 1, 11, 0xFFFFFF, 0)
        self.font.draw_text(f"{'X: {:.4f}'.format(self.player.x)}", 1, 21, 0xFFFFFF, 0)
        self.font.draw_text(f"{'Y: {:.4f}'.format(self.player.y)}", 1, 31, 0xFFFFFF, 0)
        self.font.draw_text(f"{'Z: {:.4f}'.format(self.player.z)}", 1, 41, 0xFFFFFF, 0)
        self.font.draw_text(f"Selected Tile: {self.selected_tile}", 1, 51, 0xFFFFFF, 0)
        self.font.draw_text("Press F3 to show/hide debug", 1, 71, 0xFFFFFF, 0)
        self.font.draw_text("Press 1-9 to select blocks", 1, 81, 0xFFFFFF, 0)
        self.font.draw_text("Press F7 to reload textures", 1, 91, 0xFFFFFF, 0)
        self.font.draw_text(f"Python {platform.sys.version_info.major}.{platform.sys.version_info.minor}.{platform.sys.version_info.micro}", self.window.scaled_width() - 1, 1, 0xFFFFFF, 1)
        self.font.draw_text(f"Display: {self.window.width}x{self.window.height}", self.window.scaled_width() - 1, 21, 0xFFFFFF, 1)
      else:
        self.font.draw_text("Press F3 to show debug", 1, 11, 0xFFFFFF, 0)
        self.font.draw_text("Press 1-9 to select blocks", 1, 21, 0xFFFFFF, 0)

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