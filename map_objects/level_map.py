import numpy as np
from random import randint

import tcod

from tcod.map import Map

from entities.entity_list import EntityList

from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.enum import Tiles

from map_objects.tile import CavernFloor, CavernWall, CorridorFloor, CorridorWall, Door, RoomFloor, RoomWall, ShallowWater, EmptyTile

class LevelMap(Map):
    def __init__(self, floor, console):
        width, height = floor.width, floor.height
        super().__init__(width, height, order="F")
        self.floor = floor
        self.console = console
        self.entities = EntityList(width, height)
        # TODO: Add to docstring
        self.upward_stairs_position = None
        self.downward_stairs_position = None
        # These need to be int8's to work with the tcod pathfinder
        self.explored = np.zeros((width, height), dtype=np.int8)
        self.illuminated = np.zeros((width, height), dtype=np.int8)
        self.door = np.zeros((width, height), dtype=np.int8)
        self.blocked = np.zeros((width, height), dtype=np.int8)

        self.dark_map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('dark_wall'), dtype=np.uint8
        )
        self.light_map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('light_wall'), dtype=np.uint8
        )

        self.dungeon_level = 1

        self.tiles = [[None for x in range(height)] for y in range(width)]

        self.blit_floor()

    def blit_floor(self):
        self.walkable[:] = False
        self.transparent[:] = False
        self.explored[:] = False

        for x, y, tile in self.floor:
            if self.floor.grid[x][y] == Tiles.EMPTY:
                current_tile = EmptyTile()
            elif self.floor.grid[x][y] == Tiles.OBSTACLE:
                current_tile = EmptyTile()
            elif self.floor.grid[x][y] == Tiles.IMPENETRABLE:
                current_tile = EmptyTile()
            elif self.floor.grid[x][y] == Tiles.CAVERN_WALL:
                current_tile = CavernWall()
            elif self.floor.grid[x][y] == Tiles.CORRIDOR_WALL:
                current_tile = CorridorWall()
            elif self.floor.grid[x][y] == Tiles.ROOM_WALL:
                current_tile = RoomWall()
            elif self.floor.grid[x][y] == Tiles.DOOR:
                self.make_transparent_and_walkable(x, y)
                current_tile = Door()
            elif self.floor.grid[x][y] == Tiles.DEADEND:
                current_tile = CorridorWall()
            elif self.floor.grid[x][y] == Tiles.CAVERN_FLOOR:
                self.make_transparent_and_walkable(x, y)
                current_tile = CavernFloor()
            elif self.floor.grid[x][y] == Tiles.CORRIDOR_FLOOR:
                self.make_transparent_and_walkable(x, y)
                current_tile = CorridorFloor()
            elif self.floor.grid[x][y] == Tiles.ROOM_FLOOR:
                self.make_transparent_and_walkable(x, y)
                current_tile = RoomFloor()
            elif self.floor.grid[x][y] == Tiles.SHALLOWWATER:
                current_tile = ShallowWater()
            elif self.floor.grid[x][y] == Tiles.DEEPWATER:
                current_tile = DeepWater()
            else:
                current_tile = EmptyTile()

            self.tiles[x][y] = current_tile
            self.dark_map_bg[x,y] = current_tile.out_of_fov_color
            self.light_map_bg[x,y] = current_tile.fov_color

    def make_transparent_and_walkable(self, x, y):
        self.walkable[x, y] = True
        self.transparent[x, y] = True

    def within_bounds(self, x, y, buffer=0):
        return (
            (0 + buffer <= x < self.width - buffer) and
            (0 + buffer <= y < self.height - buffer))

    def visible(self, x, y):
        return self.fov[x, y] or self.illuminated[x, y]

    def is_wall(self, x, y):
            return (not self.door[x, y]
                    and not self.transparent[x, y])

    def find_random_open_position(self):
        while True:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            if self.walkable[x, y] and not self.blocked[x, y]:
                return x, y

    def update_and_draw_all(self):
        self.console.clear()

        if not CONFIG.get('debug'):
            where_fov = np.where(self.fov[:])
            self.explored[where_fov] = True
        else:
            where_fov = np.where(self.light_map_bg[:])

        explored = np.where(self.explored[:])
        self.console.bg[explored] = self.dark_map_bg[explored]
        self.console.bg[where_fov] = self.light_map_bg[where_fov]

        for idx, x in enumerate(where_fov[0]):
            y = where_fov[1][idx]
            current_entities = self.entities.get_entities_in_position((x, y))
            entities_in_render_order = sorted(current_entities, key=lambda x: x.render_order.value)
            for entity in entities_in_render_order:
                self.console.ch[x, y] = ord(entity.char)
                self.console.fg[x, y] = entity.display_color()

    def add_entity(self, entity):
        self.entities.append(entity)
        if (entity.blocks):
            self.blocked[entity.x, entity.y] = True

    def remove_entity(self, entity):
        self.entities.remove(entity)
        if (entity.blocks):
            self.blocked[entity.x, entity.y] = False

    def move_entity(self, entity, point):
        self.entities.update_position(entity, (entity.x, entity.y), (point.x, point.y))
        if (entity.blocks):
            self.blocked[entity.x, entity.y] = False
            self.blocked[point.x, point.y] = True
