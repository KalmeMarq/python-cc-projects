from typing import Dict
from OpenGL.GL import *
import PIL.Image as Image
import numpy as np

class Texture:
  def __init__(self, path: str):
    self.__id = -1
    self.__path = path
    self.__width = 0
    self.__height = 0

  @property
  def width(self) -> int:
    return self.__width
  
  @property
  def height(self) -> int:
    return self.__height
  
  def bind(self):
    if self.__id == -1:
      self.__id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, self.__id)

  def upload_to_gpu(self):
    image = Image.open("res/" + self.__path).convert("RGBA")
    self.__width = image.width
    self.__height = image.height

    image_data = np.frombuffer(image.tobytes(), np.uint8)

    self.bind()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.__width, self.__height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glBindTexture(GL_TEXTURE_2D, 0)

  def dispose(self):
    glDeleteTextures([self.__id])
    self.__id = -1

class TextureManager:
  def __init__(self):
    self.__textures: Dict[str, Texture] = {}

  def load(self, path: str):
    texture = Texture(path)
    texture.upload_to_gpu()
    self.__textures[path] = texture

  def reload_textures(self):
    for texture in self.__textures.values():
      texture.upload_to_gpu()

  def get(self, path: str) -> Texture:
    return self.__textures[path]

  def dispose(self):
    for texture in self.__textures.values():
      texture.dispose()