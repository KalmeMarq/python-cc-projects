from OpenGL.GL import *

class RenderLayer:
  def __init__(self, index: int):
    self.__value = index

  def begin(self):
    pass

  def end(self):
    pass

  @property
  def value(self):
    return self.__value

  def __eq__(self, __value: object) -> bool:
    return isinstance(__value, RenderLayer) and __value.value == self.value

class SolidRenderLayer(RenderLayer):
  def begin(self):
    glDisable(GL_BLEND)

  def end(self):
    pass

class TranslucentRenderLayer(RenderLayer):
  def begin(self):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  def end(self):
    glDisable(GL_BLEND)

RenderLayers = {
  'SOLID': SolidRenderLayer(0),
  'TRANSLUCENT': TranslucentRenderLayer(1)
}