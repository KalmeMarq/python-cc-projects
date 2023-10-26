from OpenGL.GL import *
import json

class Font:
  def __init__(self, game):
    self.game = game
    with open("res/font.json", "r", encoding="utf-8") as f:
      self.chars = "".join(json.load(f))

  def draw_text(self, message: str, x: int, y: int, color: int, align = 0.0, shadow=True):
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
      
      idx = self.chars.find(char)

      u = (idx % 21) * 8
      v = 48 + (idx // 21) * 8

      u0 = u / 256.0
      v0 = v / 256.0
      u1 = (u + 8) / 256.0
      v1 = (v + 8) / 256.0

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