from __future__ import annotations
from typing import Dict

TILE_TYPES: Dict[int, TileType] = {}

class TileType:
  def __init__(self, tile_id: int, down_txr: int, up_txr: int, north_txr: int, south_txr: int, west_txr: int, east_txr: int, is_tickable = False, allows_light_through = False) -> None:
    self.tile_id = tile_id
    self.down_txr = down_txr
    self.up_txr = up_txr
    self.north_txr = north_txr
    self.south_txr = south_txr
    self.west_txr = west_txr
    self.east_txr = east_txr
    self.is_tickable = is_tickable
    self.allows_light_through = allows_light_through
  
  def render_in_gui(self, vertex_drawer):
    tile = self.tile_id
    x0 = 0.0
    y0 = 0.0
    z0 = 0.0
    x1 = 1.0
    y1 = 1.0
    z1 = 1.0

    if tile == 7:
      y1 -= 0.1

    u = (self.down_txr % 3) * 16
    v = self.down_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z0, u0, v0)
    vertex_drawer.vertex_uv(x1, y0, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)

    u = (self.up_txr % 3) * 16
    v = self.up_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(1.0, 1.0, 1.0, 1.0)
    vertex_drawer.vertex_uv(x1, y1, z1, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x0, y1, z1, u0, v1)

    u = (self.north_txr % 3) * 16
    v = self.north_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0
    
    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x1, y0, z0, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z0, u1, v1)

    u = (self.south_txr % 3) * 16
    v = self.south_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z1, u0, v0)
    vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z1, u1, v0)

    u = (self.west_txr % 3) * 16
    v = self.west_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z1, u1, v0)
    vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x0, y0, z0, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z1, u1, v1)

    u = (self.east_txr % 3) * 16
    v = self.east_txr // 3 * 16

    u0 = u / 48.0
    v0 = v / 64.0
    u1 = (u + 16) / 48.0
    v1 = (v + 16) / 64.0

    vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
    vertex_drawer.vertex_uv(x1, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x1, y0, z0, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y1, z1, u0, v0)

  def random_tick(self, world, x: int, y: int, z: int, tile_id: int):
    if tile_id == 7:
      if world.get_tile(x - 1, y, z) == 0:
        world.set_tile(x - 1, y, z, 7)

      if world.get_tile(x + 1, y, z) == 0:
        world.set_tile(x + 1, y, z, 7)

      if world.get_tile(x, y, z - 1) == 0:
        world.set_tile(x, y, z - 1, 7)

      if world.get_tile(x, y, z + 1) == 0:
        world.set_tile(x, y, z + 1, 7)

      if world.get_tile(x, y - 1, z) == 0:
        world.set_tile(x, y - 1, z, 7)

TILE_TYPES[1] = TileType(1, 1, 3, 0, 0, 0, 0) # GRASS BLOCK
TILE_TYPES[2] = TileType(2, 1, 1, 1, 1, 1, 1) # DIRT
TILE_TYPES[3] = TileType(3, 4, 4, 4, 4, 4, 4) # STONE
TILE_TYPES[4] = TileType(4, 2, 2, 5, 5, 5, 5) # LOG
TILE_TYPES[5] = TileType(5, 6, 6, 6, 6, 6, 6) # PLANKS
TILE_TYPES[6] = TileType(6, 7, 7, 7, 7, 7, 7) # SAND
TILE_TYPES[7] = TileType(7, 8, 8, 8, 8, 8, 8, allows_light_through=True, is_tickable=True) # WATER
TILE_TYPES[8] = TileType(8, 11, 11, 11, 11, 11, 11) # LEAVES
TILE_TYPES[9] = TileType(10, 9, 9, 9, 9, 9, 9) # FLOWER