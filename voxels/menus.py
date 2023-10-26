import random
from OpenGL.GL import *
from constants import *
import json

class Menu:
  def __init__(self, game) -> None:
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
    self.game.draw_texture(texture_name="bg.png", x=0, y=0, width=self.game.window.scaled_width(), height=self.game.window.scaled_height(), u=0, v=0, us=self.game.window.scaled_width(), vs=self.game.window.scaled_height(), tw=16, th=16, color=0x666666)
    glColor4f(1.0, 1.0, 1.0, 1.0)

  def render(self, game, mouse_pos: tuple[int, int]):
    for button in self.buttons:
      hovered = mouse_pos[0] > button[0][0] and mouse_pos[0] <= button[0][0] + button[1][0] and mouse_pos[1] > button[0][1] and mouse_pos[1] <= button[0][1] + button[1][1]
      game.draw_texture_nineslice("gui.png", button[0], button[1], (20 if hovered else 0, 22), (20, 20), (4, 4, 4, 4), 256, 256)
      game.font.draw_text(button[2], button[0][0] + button[1][0] / 2, button[0][1] + 6, 0xFFFFFF, 0.5)

class MainMenu(Menu):
  SPLASHES = ["MISSING!"]

  def __init__(self, game) -> None:
    with open("res/splashes.json", "r") as f:
      MainMenu.SPLASHES = json.load(f)
    super().__init__(game)

  def init_gui(self):
    self.splash = random.choice(MainMenu.SPLASHES)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), (200, 20), self.game.translate_key("menu.play"), self.__play)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), (200, 20), self.game.translate_key("menu.settings"), self.__settings)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), (200, 20), self.game.translate_key("menu.quit"), self.game.shutdown)

  def __play(self):
    self.game.start_world()

  def __settings(self):
    self.game.menu = SettingsMenu(self.game, self)

  def render(self, game, mouse_pos: tuple[int, int]):
    self.render_dirt_bg()
    super().render(game, mouse_pos)
    game.font.draw_text(GAME_VERSION, 1, 1, 0x888888, 0)
    game.font.draw_text("Voxel based game made by KalmeMarq", self.game.window.scaled_width() - 1, self.game.window.scaled_height() - 10, 0x888888, 1.0)
    game.font.draw_text(self.splash, game.window.scaled_width() / 2, 20, 0xFFFF00, 0.5)

class LoadingTerrainMenu(Menu):
  def __init__(self, game) -> None:
    super().__init__(game)
    self.started = False

  def render(self, game, mouse_pos: tuple[int, int]):
    self.render_dirt_bg()
    super().render(game, mouse_pos)
    game.font.draw_text("Generating terrain...", self.game.window.scaled_width() / 2, 40, 0xFFFFFF, 0.5)

    if self.started:
      self.game.load_world()

    if not self.started:
      self.started = True

class SettingsMenu(Menu):
  def __init__(self, game, parent: Menu) -> None:
    super().__init__(game)
    self.parent_menu = parent
  
  def init_gui(self):
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 48), (200, 20), f"Fog Distance: {self.__fog_distance_stringify(self.game.settings.fog_distance)}", self.__change_fog)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), (200, 20), f"Show Block Preview: {'ON' if self.game.settings.show_block_preview else 'OFF'}", self.__change_block_preview)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), (200, 20), f"V-sync: {'ON' if self.game.settings.vsync else 'OFF'}", self.__change_vsync)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), (200, 20), f"Sound: {'ON' if self.game.settings.sound_enabled else 'OFF'}", self.__change_sound)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 58), (200, 20), self.game.translate_key("menu.done"), self.__back)

  def __back(self):
    self.game.menu = self.parent_menu
    self.game.settings.save()

  def __change_fog(self):
    self.game.settings.fog_distance += 1
    if self.game.settings.fog_distance > 3:
      self.game.settings.fog_distance = 1

    self.buttons[0][2] = self.game.translate_key("menu.option_value", self.game.translate_key("menu.fog_distance"), self.__fog_distance_stringify(self.game.settings.fog_distance))

  def __change_block_preview(self):
    self.game.settings.show_block_preview = not self.game.settings.show_block_preview
    self.buttons[1][2] = f"Show Block Preview: {'ON' if self.game.settings.show_block_preview else 'OFF'}"

  def __change_vsync(self):
    self.game.settings.vsync = not self.game.settings.vsync
    self.game.window.vsync = self.game.settings.vsync
    self.buttons[2][2] = f"V-sync: {'ON' if self.game.settings.vsync else 'OFF'}"
  
  def __change_sound(self):
    self.game.settings.sound_enabled = not self.game.settings.sound_enabled
    self.buttons[3][2] = f"Sound: {'ON' if self.game.settings.sound_enabled else 'OFF'}"

  def __fog_distance_stringify(self, distance: int):
    if distance == 3:
      return self.game.translate_key("menu.fog_distance.far")
    if distance == 2:
      return self.game.translate_key("menu.fog_distance.normal")
    if distance == 1:
      return self.game.translate_key("menu.fog_distance.closest")
    return "Invalid"

  def render(self, game, mouse_pos: tuple[int, int]):
    if game.world == None:
      self.render_dirt_bg()
    else:
      game.draw_rect((0, 0), (game.window.scaled_width(), self.game.window.scaled_height()), 0x90000000)
    game.font.draw_text(self.game.translate_key("menu.settings"), game.window.scaled_width() / 2, 20, 0xFFFFFF, 0.5)
    super().render(game, mouse_pos)

class PauseMenu(Menu):
  def init_gui(self):
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), (200, 20), "Continue Game", self.__play)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), (200, 20), "Settings", self.__settings)
    self.add_button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), (200, 20), "Return To Title", self.__return_main)

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

  def render(self, game, mouse_pos: tuple[int, int]):
    game.draw_rect((0, 0), (game.window.scaled_width(), self.game.window.scaled_height()), 0x90000000)
    game.font.draw_text("Game Menu", game.window.scaled_width() / 2, 40, 0xFFFFFF, 0.5)
    super().render(game, mouse_pos)