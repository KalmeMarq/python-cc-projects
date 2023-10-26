from __future__ import annotations
from typing import Dict
import json
from utils import JSONWithCommentsDecoder

BLOCK_TYPES: Dict[int, BlockType] = {}

class BlockType:
  def __init__(self, tile_id: int, down_txr: int, up_txr: int, north_txr: int, south_txr: int, west_txr: int, east_txr: int, is_tickable = False, allows_light_through = False, is_collidable = True) -> None:
    self.tile_id = tile_id
    self.down_txr = down_txr
    self.up_txr = up_txr
    self.north_txr = north_txr
    self.south_txr = south_txr
    self.west_txr = west_txr
    self.east_txr = east_txr
    self.is_tickable = is_tickable
    self.allows_light_through = allows_light_through
    self.is_collidable = is_collidable
  
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

    u = (self.down_txr % 16) * 16
    v = self.down_txr // 16 * 16

    u0 = u / 256.0
    v0 = v / 256.0
    u1 = (u + 16) / 256.0
    v1 = (v + 16) / 256.0

    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z0, u0, v0)
    vertex_drawer.vertex_uv(x1, y0, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)

    u = (self.up_txr % 16) * 16
    v = self.up_txr // 16 * 16

    u0 = u / 256.0
    v0 = v / 256.0
    u1 = (u + 16) / 256.0
    v1 = (v + 16) / 256.0

    vertex_drawer.color(1.0, 1.0, 1.0, 1.0)
    vertex_drawer.vertex_uv(x1, y1, z1, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x0, y1, z1, u0, v1)

    u = (self.north_txr % 16) * 16
    v = self.north_txr // 16 * 16

    u0 = u / 256.0
    v0 = v / 256.0
    u1 = (u + 16) / 256.0
    v1 = (v + 16) / 256.0
    
    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z0, u1, v0)
    vertex_drawer.vertex_uv(x1, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x1, y0, z0, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z0, u1, v1)

    u = (self.south_txr % 16) * 16
    v = self.south_txr // 16 * 16

    u0 = u / 256.0
    v0 = v / 256.0
    u1 = (u + 16) / 256.0
    v1 = (v + 16) / 256.0

    vertex_drawer.color(0.6, 0.6, 0.6, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z1, u0, v0)
    vertex_drawer.vertex_uv(x0, y0, z1, u0, v1)
    vertex_drawer.vertex_uv(x1, y0, z1, u1, v1)
    vertex_drawer.vertex_uv(x1, y1, z1, u1, v0)

    u = (self.west_txr % 16) * 16
    v = self.west_txr // 16 * 16

    u0 = u / 256.0
    v0 = v / 256.0
    u1 = (u + 16) / 256.0
    v1 = (v + 16) / 256.0

    vertex_drawer.color(0.8, 0.8, 0.8, 1.0)
    vertex_drawer.vertex_uv(x0, y1, z1, u1, v0)
    vertex_drawer.vertex_uv(x0, y1, z0, u0, v0)
    vertex_drawer.vertex_uv(x0, y0, z0, u0, v1)
    vertex_drawer.vertex_uv(x0, y0, z1, u1, v1)

    u = (self.east_txr % 16) * 16
    v = self.east_txr // 16 * 16

    u0 = u / 256.0
    v0 = v / 256.0
    u1 = (u + 16) / 256.0
    v1 = (v + 16) / 256.0

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

with open("res/blocks.json") as f:
  blocks_data = json.load(f, cls=JSONWithCommentsDecoder)
  for block_data in blocks_data:
    tile_id = block_data['id']
    if isinstance(block_data.get('textures'), int):
      txr_idx = block_data.get('textures')
      down_txr = txr_idx
      up_txr = txr_idx
      north_txr = txr_idx
      south_txr = txr_idx
      west_txr = txr_idx
      east_txr = txr_idx
    else:
      down_txr = block_data['textures']['down']
      up_txr = block_data['textures']['up']
      north_txr = block_data['textures']['north']
      south_txr = block_data['textures']['south']
      west_txr = block_data['textures']['west']
      east_txr = block_data['textures']['east']
    is_tickable = block_data.get('is_tickable') if block_data.get('is_tickabke') != None else False 
    allows_light_through = block_data.get('allows_light_through') if block_data.get('allows_light_through') != None else False
    is_collidable = block_data.get('is_collidable') if block_data.get('is_collidable') != None else True

    BLOCK_TYPES[tile_id] = BlockType(tile_id, down_txr, up_txr, north_txr, south_txr, west_txr, east_txr, is_tickable, allows_light_through, is_collidable)