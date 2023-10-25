from typing import Callable
from OpenGL.GL import *

class RenderLayer:
  def __init__(self, index: int, begin_callback: Callable[[], None], end_callback: Callable[[], None]):
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