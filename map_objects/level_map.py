import numpy as np
from random import randint

import tcod

from tcod.map import Map

from entities.entity_list import EntityList

from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.enum import RoutingOptions, Tiles

from map_objects.point import Point
from map_objects.tile import CavernFloor, CavernWall, CorridorFloor, CorridorWall, Door, RoomFloor, RoomWall, ShallowWater, StairsFloor, EmptyTile

class LevelMap(Map):
    def __init__(self, floor):
        width, height = floor.width, floor.height
        super().__init__(width, height, order="F")
        self.floor = floor
        self.entities = EntityList(width, height)
        # TODO: Add to docstring
        self.upward_stairs_position = None
        self.downward_stairs_position = None
        # These need to be int8's to work with the tcod pathfinder
        self.explored = np.zeros((width, height), dtype=np.int8)
        self.illuminated = np.zeros((width, height), dtype=np.int8)
        self.door = np.zeros((width, height), dtype=np.int8)
        self.blocked = np.zeros((width, height), dtype=np.int8)
        self.caves = np.zeros((width, height), dtype=np.int8)
        self.corridors = np.zeros((width, height), dtype=np.int8)
        self.floors = np.zeros((width, height), dtype=np.int8)
        self.allowed_stairs_tiles = np.zeros((width, height), dtype=np.int8)

        self.dark_map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('dark_wall'), dtype=np.uint8
        )
        self.light_map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('light_wall'), dtype=np.uint8
        )

        self.dungeon_level = 1

        self.tiles = [[None for x in range(height)] for y in range(width)]

        self.blit_floor()

        self.paths = []
        self.walkables = []

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
                self.door[x,y] = True
                self.make_transparent_and_walkable(x, y)
                current_tile = Door()
            elif self.floor.grid[x][y] == Tiles.DEADEND:
                current_tile = CorridorWall()
            elif self.floor.grid[x][y] == Tiles.CAVERN_FLOOR:
                self.caves[x,y] = True
                self.make_transparent_and_walkable(x, y)
                current_tile = CavernFloor()
            elif self.floor.grid[x][y] == Tiles.CORRIDOR_FLOOR:
                self.caves[x,y] = False
                self.corridors[x,y] = True
                self.make_transparent_and_walkable(x, y)
                current_tile = CorridorFloor()
            elif self.floor.grid[x][y] == Tiles.ROOM_FLOOR:
                self.caves[x,y] = False
                self.floors[x,y] = True
                self.make_transparent_and_walkable(x, y)
                current_tile = RoomFloor()
            elif self.floor.grid[x][y] == Tiles.SHALLOWWATER:
                current_tile = ShallowWater()
            elif self.floor.grid[x][y] == Tiles.DEEPWATER:
                current_tile = DeepWater()
            elif self.floor.grid[x][y] == Tiles.STAIRSFLOOR:
                self.allowed_stairs_tiles[x,y] = True
                current_tile = RoomFloor()
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

    def find_random_open_position(self, routing_avoid=[], room = None):
        routing_avoid.append(RoutingOptions.AVOID_BLOCKERS)
        possible_positions = self.make_walkable_array(routing_avoid)

        start_x = 0
        end_x = self.width - 1
        start_y = 0
        end_y = self.height - 1

        if room:
            start_x = room.x
            end_x = room.x+room.width
            start_y = room.y
            end_y = room.y+room.height

        while True:
            x = randint(start_x, end_x)
            y = randint(start_y, end_y)
            if possible_positions[x, y]:
                return Point(x, y)

    def update_and_draw_all(self, map_console):
        map_console.clear()

        if not CONFIG.get('debug'):
            where_fov = np.where(self.fov[:])
            self.explored[where_fov] = True
        else:
            where_fov = np.where(self.light_map_bg[:])

        explored = np.where(self.explored[:])
        map_console.bg[explored] = self.dark_map_bg[explored]
        map_console.bg[where_fov] = self.light_map_bg[where_fov]
        if CONFIG.get('debug'):
            for current_path in self.paths:
                for x,y in current_path:
                    map_console.bg[x,y] = tcod.lighter_green

            self.paths.clear()

            for current_walkable in self.walkables:
                for x, y, _ in self.floor:
                    if (current_walkable[x, y]):
                        map_console.bg[x,y] = tcod.lighter_blue

            self.walkables.clear()

        for idx, x in enumerate(where_fov[0]):
            y = where_fov[1][idx]
            current_entities = self.entities.get_entities_in_position((x, y))
            entities_in_render_order = sorted(current_entities, key=lambda x: x.render_order.value)
            for entity in entities_in_render_order:
                map_console.ch[x, y] = ord(entity.char)
                map_console.fg[x, y] = entity.display_color()

    def add_entity(self, entity):
        self.entities.append(entity)
        if (entity.blocks):
            self.blocked[entity.x, entity.y] = True

    def remove_entity(self, entity):
        self.entities.remove(entity)
        if (entity.blocks):
            self.blocked[entity.x, entity.y] = False

            current_entities = self.entities.get_entities_in_position((entity.x, entity.y))

            for other_entity in current_entities:
                if other_entity.blocks:
                    self.blocked[entity.x, entity.y] = True

    def move_entity(self, entity, point):
        self.entities.update_position(entity, (entity.x, entity.y), (point.x, point.y))
        if (entity.blocks):
            self.blocked[entity.x, entity.y] = False

            current_entities = self.entities.get_entities_in_position((entity.x, entity.y))

            for other_entity in current_entities:
                if other_entity.blocks:
                    self.blocked[entity.x, entity.y] = True

            self.blocked[point.x, point.y] = True

    def make_walkable_array(self, routing_avoid=None):
        """Return a boolean array indicating which squares are accable to be routed
        through for some entity.

        Parameters
        ----------
        game_map: GameMap object

        routing_avoid: List of RoutingOptions
          A list containing square types which need to be avoided during routing.

        Returns
        -------
        valid_to_route: np.array or bool
          A boolean array indicating which squares are valid to route through.
        """
        if not routing_avoid:
            routing_avoid = []
        walkable = self.walkable.copy()
        if RoutingOptions.AVOID_BLOCKERS in routing_avoid:
            walkable = walkable * (1 - self.blocked)
        if RoutingOptions.AVOID_CAVES in routing_avoid:
            walkable = walkable * (1 - self.caves)
        if RoutingOptions.AVOID_CORRIDORS in routing_avoid:
            walkable = walkable * (1 - self.corridors)
        if RoutingOptions.AVOID_DOORS in routing_avoid:
            walkable = walkable * (1 - self.door)
        if RoutingOptions.AVOID_FLOORS in routing_avoid:
            walkable = walkable * (1 - self.floors)
        if RoutingOptions.AVOID_FOV in routing_avoid:
            walkable = walkable * (1 - self.fov)
        #if RoutingOptions.AVOID_WATER in routing_avoid:
        #    walkable = walkable * (1 - self.water)
        #if RoutingOptions.AVOID_FIRE in routing_avoid:
        #    walkable = walkable * (1 - self.fire)
        #if RoutingOptions.AVOID_STEAM in routing_avoid:
        #    walkable = walkable * (1 - self.steam)
        if RoutingOptions.AVOID_STAIRS in routing_avoid:
            if self.upward_stairs_position:
                walkable[self.upward_stairs_position] = False
            if self.downward_stairs_position:
                walkable[self.downward_stairs_position] = False
        return walkable

    def walkable_for_entity_under_mouse(self, mouse):
        if self.within_bounds(mouse.cx, mouse.cy):
            current_entities = self.entities.get_entities_in_position((mouse.cx, mouse.cy))
            for entity in current_entities:
                entity_walkable = self.make_walkable_array(entity.movement.routing_avoid)
                self.walkables.append(entity_walkable)

    def find_closest_entity(self, point, range = 2, species_type = None):
        return self.entities.find_closest(point, species_type, max_distance=range)
