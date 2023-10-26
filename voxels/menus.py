import glfw
import random
from OpenGL.GL import *
from constants import *
import json

class Widget:
  def __init__(self) -> None:
    pass

  def is_pressable(self):
    return False

  def render(self, game, mouse_pos: tuple[int, int]):
    pass

class ColoredCustomRenderer(Widget):
  def __init__(self, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (1, 1), colors: list[int] = [0xFFFFFFFF], orientation: str = "vertical") -> None:
    super().__init__()
    self.pos = pos
    self.size = size
    self.colors = colors
    self.orientation = orientation

  def render(self, game, mouse_pos: tuple[int, int]):
    game.draw_rect(self.pos, self.size, self.colors[0])

class Image(Widget):
  def __init__(self, texture_name: str, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (1, 1), color: int = 0xFFFFFF, uv: tuple[int, int] = (0, 0), uv_size: tuple[int, int] | None = None, nineslice: int | tuple[int, int] | tuple[int, int, int, int] | None = None, base_size: tuple[int, int] | None = None) -> None:
    super().__init__()
    self.texture_name = texture_name
    self.pos = pos
    self.size = size
    self.color = color
    self.uv = uv
    self.uv_size = uv_size
    self.nineslice = nineslice
    self.base_size = base_size

  def render(self, game, mouse_pos: tuple[int, int]):
    texture = game.texture_manager.get(self.texture_name)
    tw = texture.width if self.base_size == None else self.base_size[0]
    th = texture.height if self.base_size == None else self.base_size[1]
    us = tw if self.uv_size == None else self.uv_size[0]
    vs = th if self.uv_size == None else self.uv_size[1]

    game.draw_texture(self.texture_name, x=self.pos[0], y=self.pos[1], width=self.size[0], height=self.size[1], u=self.uv[0], v=self.uv[1], us=us, vs=vs, tw=tw, th=th, color=self.color)
    glColor4f(1.0, 1.0, 1.0, 1.0)

class Text(Widget):
  def __init__(self, pos: tuple[int, int] = (0, 0), message: str = "", align = 0.0, color = 0xFFFFFF, hover_color: int | None = None):
    super().__init__()
    self.pos = pos
    self.message = message
    self.align = align
    self.color = color
    self.hover_color = color if hover_color == None else hover_color

  def render(self, game, mouse_pos: tuple[int, int]):
     game.font.draw_text(self.message, self.pos[0], self.pos[1], self.color, self.align)

class Toggle(Widget):
  def __init__(self, setter, getter, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (200, 20), message: str = ""):
    super().__init__()
    self.setter = setter
    self.getter = getter
    self.value = getter()
    self.pos = pos
    self.size = size
    self.message = message

  def is_pressable(self):
    return True
  
  def press(self):
    self.value = not self.value
    self.setter(self.value)
    self.value = self.getter()

  def is_cursor_over(self, mouse_pos: tuple[int, int]):
    return mouse_pos[0] > self.pos[0] and mouse_pos[0] <= self.pos[0] + self.size[0] and mouse_pos[1] > self.pos[1] and mouse_pos[1] <= self.pos[1] + self.size[1]

  def render(self, game, mouse_pos: tuple[int, int]):
    hovered = self.is_cursor_over(mouse_pos)
    game.draw_texture_nineslice("gui.png", self.pos, self.size, (20 if hovered else 0, 22), (20, 20), (4, 4, 4, 4), 256, 256)
    game.font.draw_text(self.message + ": " + (game.translate_key("menu.on") if self.value else game.translate_key("menu.off")), self.pos[0] + self.size[0] / 2, self.pos[1] + 6, 0xFFFFFF, 0.5)

class CycleButton(Widget):
  def __init__(self, value, values, value_to_string, setter, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (200, 20), message: str = ""):
    super().__init__()
    self.pos = pos
    self.size = size
    self.message = message
    self.idx = values.index(value)
    self.value = value
    self.values = values
    self.value_to_string = value_to_string
    self.setter = setter

  def is_pressable(self):
    return True
  
  def press(self):
    self.idx = (self.idx + 1) % len(self.values)
    self.value = self.values[self.idx]
    self.setter(self.value)

  def is_cursor_over(self, mouse_pos: tuple[int, int]):
    return mouse_pos[0] > self.pos[0] and mouse_pos[0] <= self.pos[0] + self.size[0] and mouse_pos[1] > self.pos[1] and mouse_pos[1] <= self.pos[1] + self.size[1]

  def render(self, game, mouse_pos: tuple[int, int]):
    hovered = self.is_cursor_over(mouse_pos)
    game.draw_texture_nineslice("gui.png", self.pos, self.size, (20 if hovered else 0, 22), (20, 20), (4, 4, 4, 4), 256, 256)
    game.font.draw_text(self.message + ": " + self.value_to_string(self.value), self.pos[0] + self.size[0] / 2, self.pos[1] + 6, 0xFFFFFF, 0.5)

class Button(Widget):
  def __init__(self, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (200, 20), message: str = "") -> None:
    super().__init__()
    self.pos = pos
    self.size = size
    self.message = message
    self.__press_callback = None

  def is_pressable(self):
    return True

  def press_func(self, callback):
    self.__press_callback = callback
    return self

  def press(self):
    if self.__press_callback != None:
      self.__press_callback(self)

  def is_cursor_over(self, mouse_pos: tuple[int, int]):
    return mouse_pos[0] > self.pos[0] and mouse_pos[0] <= self.pos[0] + self.size[0] and mouse_pos[1] > self.pos[1] and mouse_pos[1] <= self.pos[1] + self.size[1]

  def render(self, game, mouse_pos: tuple[int, int]):
    hovered = self.is_cursor_over(mouse_pos)
    game.draw_texture_nineslice("gui.png", self.pos, self.size, (20 if hovered else 0, 22), (20, 20), (4, 4, 4, 4), 256, 256)
    game.font.draw_text(self.message, self.pos[0] + self.size[0] / 2, self.pos[1] + 6, 0xFFFFFF, 0.5)

class Menu:
  def __init__(self, game, parent = None) -> None:
    self.game = game
    self.parent = parent
    self.widgets = []

  def on_display(self):
    self.widgets = []
    self.init_gui()

  def on_remove(self):
    pass

  def resize(self):
    self.widgets.clear()
    self.init_gui()
  
  def init_gui(self):
    pass

  def key_pressed(self, key):
    if key == glfw.KEY_ESCAPE and not isinstance(self, MainMenu)and not isinstance(self, PauseMenu):
      self.game.menu = self.parent

  def add_button(self, pos: tuple[int, int], size: tuple[int, int], text: str, callback):
    self.buttons.append([pos, size, text, callback])

  def mouse_clicked(self, mouse_pos: tuple[int, int]):
    for widget in self.widgets:
      if widget.is_pressable() and widget.is_cursor_over(mouse_pos):
        self.game.play_sound(self.game.click_sound)
        widget.press()
        break

  def render_dirt_bg(self):
    self.game.draw_texture(texture_name="bg.png", x=0, y=0, width=self.game.window.scaled_width(), height=self.game.window.scaled_height(), u=0, v=0, us=self.game.window.scaled_width(), vs=self.game.window.scaled_height(), tw=16, th=16, color=0x666666)
    glColor4f(1.0, 1.0, 1.0, 1.0)

  def render(self, game, mouse_pos: tuple[int, int]):
    for widget in self.widgets:
      widget.render(self.game, mouse_pos)

class MainMenu(Menu):
  SPLASHES = ["MISSING!"]

  def __init__(self, game) -> None:
    with open("res/splashes.json", "r") as f:
      MainMenu.SPLASHES = json.load(f)
    super().__init__(game)

  def init_gui(self):
    self.splash = random.choice(MainMenu.SPLASHES)
    self.widgets.append(Image("bg.png", size=(self.game.window.scaled_width(), self.game.window.scaled_height()), uv_size=(self.game.window.scaled_width(), self.game.window.scaled_height()), color=0x666666))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), message=self.game.translate_key("menu.play")).press_func(lambda _ : self.__play()))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), message=self.game.translate_key("menu.settings")).press_func(lambda _ : self.__settings()))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), message=self.game.translate_key("menu.quit")).press_func(lambda _ : self.game.shutdown()))
    self.widgets.append(Text((1, 1), GAME_VERSION, color=0x888888))
    self.widgets.append(Text((self.game.window.scaled_width() - 1, self.game.window.scaled_height() - 10), "Voxel based game made by KalmeMarq", color=0x888888, align=1))
    self.widgets.append(Text((self.game.window.scaled_width() / 2, 20), self.splash, color=0xFFFF00, align=0.5))

  def __play(self):
    self.game.start_world()

  def __settings(self):
    self.game.menu = SettingsMenu(self.game, self)

class SelectWorld(Menu):
  def __init__(self, game, parent: Menu) -> None:
    super().__init__(game)
    self.parent_menu = parent

  def init_gui(self):
    self.widgets.append(Image("bg.png", size=(self.game.window.scaled_width(), self.game.window.scaled_height()), uv_size=(self.game.window.scaled_width(), self.game.window.scaled_height()), color=0x666666))

class CreateWorld(Menu):
  pass

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
    super().__init__(game, parent)
  
  def init_gui(self):
    if self.game.world == None:
      self.widgets.append(Image("bg.png", size=(self.game.window.scaled_width(), self.game.window.scaled_height()), uv_size=(self.game.window.scaled_width(), self.game.window.scaled_height()), color=0x666666))
    else:
      self.widgets.append(ColoredCustomRenderer(size=(self.game.window.scaled_width(), self.game.window.scaled_height()), colors=[0x90000000]))
    self.widgets.append(Text((self.game.window.scaled_width() / 2, 20), self.game.translate_key("menu.settings"), align=0.5))
    self.widgets.append(Toggle(self.__set_block_preview, lambda : self.game.settings.show_block_preview, pos=(self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 48), message=self.game.translate_key("menu.block_preview")))
    self.widgets.append(Toggle(self.__set_sound, lambda : self.game.settings.sound_enabled, pos=(self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), message=self.game.translate_key("menu.sound")))
    self.widgets.append(Toggle(self.__set_vsync, lambda : self.game.settings.vsync, pos=(self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), message=self.game.translate_key("menu.vsync")))
    self.widgets.append(CycleButton(self.game.settings.fog_distance, [1, 2, 3], self.__fog_distance_stringify, self.__set_fog_distance, pos = (self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), message=self.game.translate_key("menu.fog_distance")))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 58), message=self.game.translate_key("menu.done")).press_func(lambda _ : self.__back()))

  def __set_block_preview(self, value):
    self.game.settings.show_block_preview = value

  def __set_sound(self, value):
    self.game.settings.sound_enabled = value

  def __set_vsync(self, value):
    self.game.settings.vsync = value
    self.game.window.vsync = self.game.settings.vsync

  def __set_fog_distance(self, value):
    self.game.settings.fog_distance = value

  def __back(self):
    self.game.menu = self.parent
    self.game.settings.save()

  def __fog_distance_stringify(self, distance: int):
    if distance == 3:
      return self.game.translate_key("menu.fog_distance.far")
    if distance == 2:
      return self.game.translate_key("menu.fog_distance.normal")
    if distance == 1:
      return self.game.translate_key("menu.fog_distance.closest")
    return "Invalid"

class PauseMenu(Menu):
  def init_gui(self):
    self.widgets.append(ColoredCustomRenderer(size=(self.game.window.scaled_width(), self.game.window.scaled_height()), colors=[0x90000000]))
    self.widgets.append(Text((self.game.window.scaled_width() / 2, 40), message=self.game.translate_key("menu.game_menu"), align=0.5))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 - 24), message=self.game.translate_key("menu.continue_game")).press_func(lambda _ : self.__play()))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2), message=self.game.translate_key("menu.settings")).press_func(lambda _ : self.__settings()))
    self.widgets.append(Button((self.game.window.scaled_width() / 2 - 100, self.game.window.scaled_height() / 2 + 24), message=self.game.translate_key("menu.return_to_title")).press_func(lambda _ : self.__return_main()))

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