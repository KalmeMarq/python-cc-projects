import glfw
from typing import Dict
from OpenGL.GL import *
import PIL.Image as Image
import math
from utils import perspective
import numpy as np

class TextureManager:
  def __init__(self):
    self.textures: Dict[str, np.uintc] = {}

  def load(self, path: str) -> None:
    im = Image.open(path);
    imdata = np.frombuffer(im.convert("RGB").tobytes(), np.uint8)

    txr_id = glGenTextures(1)
    print(type(txr_id))
    glBindTexture(GL_TEXTURE_2D, txr_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.width, im.height, 0, GL_RGB, GL_UNSIGNED_BYTE, imdata)
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
    self.y = 0
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
      self.rot_x = 90.0

class Game:
  def __init__(self):
    if not glfw.init():
      exit(0)

    glfw.default_window_hints()
    self.window = glfw.create_window(800, 600, "Voxels", None, None)
    imicon = Image.open("icon.png")
    glfw.set_window_icon(self.window, 1, [imicon])
    glfw.make_context_current(self.window)
    glfw.swap_interval(1)

    self.texture_manager = TextureManager()
    self.texture_manager.load('grass.png')

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

    self.tiles = np.zeros(16 * 16 * 16, dtype=np.uint8)

    for x in range(16):
      for y in range(16):
        for z in range(16):
          self.tiles[(y * 16 + z) * 16 + x] = 1

  def get_tile(self, x: int, y: int, z: int):
    if x < 0 or x >= 16 or y < 0 or y >= 16 or z < 0 or z >= 16:
      return 0
    return self.tiles[(y * 16 + z) * 16 + x]

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
    self.proj_mat = perspective(1.22172, 800.0 / 600.0, 0.05, 1000.0)
    tick_last_time = glfw.get_time()
    glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)

    while self.running:
      if glfw.window_should_close(self.window):
        self.running = False

      tick_now = glfw.get_time()
      tick_passed_sec = tick_now - tick_last_time
      tick_last_time = tick_now
      ticks = int(tick_passed_sec * 60 / 1.0)

      for _ in range(0, ticks):
        self.tick()

      self.player.turn(self.mouse['dx'], self.mouse['dy'])
      self.mouse['dx'] = 0
      self.mouse['dy'] = 0
      
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

      self.render()
      
      glfw.swap_buffers(self.window)
      glfw.poll_events()

      frame_counter += 1

      now = glfw.get_time()
      if now - last_time > 1.0:
        last_time = now
        glfw.set_window_title(self.window, f"Voxels {frame_counter} FPS Player({self.player.x},{self.player.y},{self.player.z})")
        frame_counter = 0

    self.texture_manager.dispose()
    glfw.terminate()

  def render(self):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glLoadMatrixf(self.proj_mat)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(self.player.rot_x, 1.0, 0.0, 0.0);
    glRotatef(self.player.rot_y, 0.0, 1.0, 0.0);
    glTranslatef(-self.player.x, -self.player.y, -self.player.z)

    glEnable(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, self.texture_manager.get("grass.png"))

    for y in range(16):
      for x in range(16):
        for z in range(16):
          if y == 0:
            u0 = 16.0 / 32.0
            v0 = 16.0 / 32.0
            u1 = 32.0 / 32.0
            v1 = 32.0 / 32.0
          else:
            u0 = 0
            v0 = 0 
            u1 = 16.0 / 32.0
            v1 = 16.0 / 32.0 

          x0 = x
          y0 = y
          z0 = z
          x1 = x + 1.0
          y1 = y + 1.0
          z1 = z + 1.0
          glBegin(GL_QUADS)

          if self.get_tile(x, y - 1, z) == 0:
            glColor4f(0.6, 0.6, 0.6, 1.0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y0, z1)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y0, z0)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y0, z0)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y0, z1)

          if self.get_tile(x, y + 1, z) == 0:
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glTexCoord2f(u1, v1)
            glVertex3f(x1, y1, z1)
            glTexCoord2f(u1, v0)
            glVertex3f(x1, y1, z0)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y1, z0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y1, z1) 

          if self.get_tile(x, y, z + 1) == 0:
            glColor4f(0.6, 0.6, 0.6, 1.0)
            glTexCoord2f(u1, v1)
            glVertex3f(x0, y0, z0)
            glTexCoord2f(u1, v0)
            glVertex3f(x0, y1, z0)
            glTexCoord2f(u0, v0)
            glVertex3f(x1, y1, z0)
            glTexCoord2f(u0, v1)
            glVertex3f(x1, y0, z0)

          if self.get_tile(x - 1, y, z) == 0:
            glColor4f(0.8, 0.8, 0.8, 1.0)
            glTexCoord2f(u1, v0)
            glVertex3f(x0, y1, z1)
            glTexCoord2f(u0, v0)
            glVertex3f(x0, y1, z0)
            glTexCoord2f(u0, v1)
            glVertex3f(x0, y0, z0)
            glTexCoord2f(u1, v1)
            glVertex3f(x0, y0, z1)

          if self.get_tile(x + 1, y, z) == 0:
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