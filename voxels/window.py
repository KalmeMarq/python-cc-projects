from typing import Callable
import glfw
import PIL.Image as Image

class GameWindow:
  def __init__(self, width: int, height: int):
    self.__width = width
    self.__height = height
    self.__mouse_button_callback: Callable[[int, int], None] | None = None
    self.__scroll_callback: Callable[[float, float], None] | None = None
    self.__size_changed_callback: Callable[[], None] | None = None
    self.__scale_factor = 2

  def init(self, title: str) -> bool:
    if not glfw.init():
      exit()

    glfw.default_window_hints()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    self.__handle = glfw.create_window(self.__width, self.__height, title, None, None)
    self.set_icon("icon.png")

    glfw.make_context_current(self.__handle)
    glfw.swap_interval(1)
    glfw.show_window(self.__handle)

    glfw.set_framebuffer_size_callback(self.__handle, lambda _, w, h: self.__on_framebuffer_size_changed(w, h))
    glfw.set_mouse_button_callback(self.__handle, lambda _, button, action, mods : self.__mouse_button_callback(button, action) if self.__mouse_button_callback != None else None)
    glfw.set_scroll_callback(self.__handle, lambda _, x_offset, y_offset : self.__scroll_callback(x_offset, y_offset) if self.__scroll_callback != None else None)

  def mouse_button_func(self, callback: Callable[[int, int], None]):
    self.__mouse_button_callback = callback
  
  def scroll_func(self, callback: Callable[[float, float], None]):
    self.__scroll_callback = callback
  
  def size_changed_func(self, callback: Callable[[], None]):
    self.__size_changed_callback = callback

  def __on_framebuffer_size_changed(self, new_width: int, new_height: int):
    self.__width = new_width
    self.__height = new_height

    if self.__width > 1000 and self.__height > 800:
      self.__scale_factor = 3
    else:
      self.__scale_factor = 2

    if self.__size_changed_callback != None:
      self.__size_changed_callback()

  @property
  def handle(self):
    return self.__handle

  @property
  def width(self) -> int:
    return self.__width
  
  @property
  def height(self) -> int:
    return self.__height
  
  @property
  def scale_factor(self) -> int:
    return self.__scale_factor
  
  def scaled_width(self) -> int:
    return int(self.__width / self.__scale_factor)
  
  def scaled_height(self) -> int:
    return int(self.__height / self.__scale_factor)

  def set_icon(self, path: str):
    image = Image.open("res/" + path)
    glfw.set_window_icon(self.__handle, 1, [image])

  def should_close(self) -> bool:
    return glfw.window_should_close(self.__handle)

  def update_frame(self):
    glfw.swap_buffers(self.__handle)
    glfw.poll_events()