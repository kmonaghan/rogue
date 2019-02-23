import numpy as np

import tcod

from tcod.map import Map

from entities.entity_list import EntityList

from etc.colors import COLORS
from etc.enum import Tiles

from map_objects.tile import CavernFloor, CavernWall, CorridorFloor, CorridorWall, Door, RoomFloor, RoomWall, EmptyTile

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

        self.blit_floor()

    def blit_floor(self):
        self.walkable[:] = False
        self.transparent[:] = False
        self.explored[:] = True

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

    def update_and_draw_all(self, recompute, player):
        self.console.clear()

        if recompute:
            self.compute_fov(player.x, player.y, 10, True, 0,)
        self.console.bg[:] = self.dark_map_bg[:]

        where_fov = np.where(self.fov[:])
        self.console.bg[where_fov] = self.light_map_bg[where_fov]

        self.console.ch[player.x, player.y] = ord(player.char)
        self.console.fg[player.x, player.y] = player.display_color()

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    def move_entity(self, entity, point):
        self.entities.update_position(entity, point.x, point.y)
