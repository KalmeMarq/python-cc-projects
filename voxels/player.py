import random
import math
import glfw
from utils import AABB

class Player:
  WIDTH = 0.6
  HEIGHT = 1.8

  def __init__(self, world):
    self.world = world
    self.x = 9
    self.y = 20
    self.z = 9
    self.old_x = 0
    self.old_y = 0
    self.old_z = 0
    self.rot_x = 0
    self.rot_y = 0
    self.on_ground = False
    self.xd = 0
    self.yd = 0
    self.zd = 0
    self.is_inside_water = False
    self.bounding_box = AABB(self.x - Player.WIDTH / 2, self.y - Player.HEIGHT / 2, self.z - Player.WIDTH / 2, self.x + Player.WIDTH / 2, self.y + Player.HEIGHT / 2, self.z + Player.WIDTH / 2)

  def reset_pos(self):
    self.x = random.randint(0, 4 * 16)
    self.y = 64
    self.z = random.randint(0, 4 * 16)
    self.bounding_box = AABB(self.x - Player.WIDTH / 2, self.y - Player.HEIGHT / 2, self.z - Player.WIDTH / 2, self.x + Player.WIDTH / 2, self.y + Player.HEIGHT / 2, self.z + Player.WIDTH / 2)

  def tick(self):
    self.old_x = self.x
    self.old_y = self.y
    self.old_z = self.z

    xa = 0.0
    za = 0.0

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_R) != glfw.RELEASE:
      self.reset_pos()

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_W) != glfw.RELEASE:
      za -= 1
    
    if glfw.get_key(self.world.game.window.handle, glfw.KEY_S) != glfw.RELEASE:
      za += 1

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_A) != glfw.RELEASE:
      xa -= 1
    
    if glfw.get_key(self.world.game.window.handle, glfw.KEY_D) != glfw.RELEASE:
      xa += 1

    if glfw.get_key(self.world.game.window.handle, glfw.KEY_SPACE) != glfw.RELEASE and self.on_ground:
      self.yd = 0.12

    camera_pos = [self.x, self.bounding_box.y0, self.z]
    self.is_inside_water = self.world.get_tile(int(camera_pos[0]), int(camera_pos[1]), int(camera_pos[2])) == 7

    mov_speed = 0.005
    if self.on_ground:
      mov_speed = 0.02
    
    if self.is_inside_water:
      mov_speed *= 0.4

    self.move_relative(xa, za, mov_speed)
    self.yd = self.yd - 0.005
    self.move(self.xd, self.yd, self.zd)
    self.xd *= 0.91
    self.yd *= 0.98
    self.zd *= 0.91
    if self.on_ground:
      self.xd *= 0.8
      self.zd *= 0.8

  # O código de colisão não foi totalmente feito por mim
  # Obtiu por pesquisa e basiado no Minecraft
  def move(self, xa: float, ya: float, za: float):
    xa_ini = xa
    ya_ini = ya
    za_ini = za

    cube_boxes = self.world.get_cubes(self.bounding_box.expand(xa, ya, za))

    for i in range(len(cube_boxes)):
      ya = cube_boxes[i].clipYCollide(self.bounding_box, ya)
    
    self.bounding_box.move(0.0, ya, 0.0)

    for i in range(len(cube_boxes)):
      xa = cube_boxes[i].clipXCollide(self.bounding_box, xa)
    
    self.bounding_box.move(xa, 0.0, 0.0)

    for i in range(len(cube_boxes)):
      za = cube_boxes[i].clipZCollide(self.bounding_box, za)

    self.bounding_box.move(0.0, 0.0, za)

    self.on_ground = ya_ini != ya and ya_ini < 0.0

    if xa_ini != xa:
      self.xd = 0.0

    if ya_ini != ya:
      self.yd = 0.0

    if za_ini != za:
      self.zd = 0.0

    self.x = (self.bounding_box.x0 + self.bounding_box.x1) / 2.0
    self.y = self.bounding_box.y0 + 1.62
    self.z = (self.bounding_box.z0 + self.bounding_box.z1) / 2.0

  def move_relative(self, xa, za, speed):
    dist = xa * xa + za * za
    if dist >= 0.01:
      dist = speed / math.sqrt(dist)
      xa *= dist
      za *= dist

      psin = math.sin(self.rot_y * math.pi / 180.0)
      pcos = math.cos(self.rot_y * math.pi / 180.0)

      self.xd += xa * pcos - za * psin
      self.zd += za * pcos + xa * psin

  def turn(self, xr, yr):
    self.rot_y = self.rot_y + xr * 0.15
    self.rot_x = self.rot_x - yr * 0.15

    if self.rot_x < -90.0:
      self.rot_x = -90.0

    if self.rot_x > 90.0:
      self.rot_x = 90.0