import numpy as np
from random import randint

import tcod

from tcod.map import Map

from entities.entity_list import EntityList

from etc.colors import COLORS, random_color_shimmer
from etc.configuration import CONFIG
from etc.enum import RoutingOptions, Tiles, WALKABLE_TILES, SHIMMERING_TILES

from map_objects.point import Point
from map_objects.tile import (CavernFloor, CavernWall, CorridorFloor,
                                CorridorWall, DeepWater, Door, FungalCavernFloor,
                                ImpenetrableTile, RoomFloor, RoomWall,
                                ShallowWater, StairsFloor, EmptyTile,
                                PotentialCorridorFloor)

from utils.utils import matprint

class LevelMap(Map):
    def __init__(self, grid, rooms = []):
        width, height = grid.shape
        super().__init__(width, height, order="F")
        self.entities = EntityList(width, height)
        # TODO: Add to docstring

        # These need to be int8's to work with the tcod pathfinder
        self.grid = np.zeros(self.walkable.shape, dtype=np.int8)
        self.explored = np.zeros(self.walkable.shape, dtype=np.int8)
        self.illuminated = np.zeros(self.walkable.shape, dtype=np.int8)
        self.blocked = np.zeros(self.walkable.shape, dtype=np.int8)
        self.npc_fov = self.fov

        self.dark_map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('dark_default'), dtype=np.uint8
        )
        self.light_map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('light_default'), dtype=np.uint8
        )
        self.map_bg = np.full(
            self.walkable.shape + (3,), COLORS.get('console_background'), dtype=np.uint8
        )
        self.map_fg = np.full(
            self.walkable.shape + (3,), COLORS.get('foreground_default'), dtype=np.uint8
        )

        self.map_char = np.zeros(self.walkable.shape, dtype=np.int8)

        self.dungeon_level = 1

        self.tiles = [[None for x in range(height)] for y in range(width)]

        self.blit_floor(grid)

        self.paths = []
        self.walkables = []

        self.torch = True
        self.noise = None
        self.torchx = 0.0
        # 1d noise for the torch flickering
        self.noise = tcod.noise_new(1, 1.0, 1.0)

        self.dijkstra_player = None
        self.dijkstra_flee = None

        self.rooms = rooms

        self.should_shimmer = 0

    @property
    def caves(self):
        return self.tiles_of_type(Tiles.CAVERN_FLOOR)

    @property
    def corridors(self):
        return self.tiles_of_type(Tiles.CORRIDOR_FLOOR)

    @property
    def doors(self):
        return self.tiles_of_type(Tiles.DOOR)

    @property
    def floors(self):
        return self.tiles_of_type(Tiles.ROOM_FLOOR)

    def tiles_of_type(self, tile):
        return np.where(self.grid == tile)

    def blit_floor(self, grid):
        self.walkable[:] = False
        self.transparent[:] = False
        self.explored[:] = False

        for (x,y), value in np.ndenumerate(grid):
            if grid[x,y] == Tiles.EMPTY:
                current_tile = EmptyTile()
            elif grid[x,y] == Tiles.OBSTACLE:
                current_tile = EmptyTile()
            elif grid[x,y] == Tiles.IMPENETRABLE:
                current_tile = ImpenetrableTile()
            elif grid[x,y] == Tiles.CAVERN_WALL:
                current_tile = CavernWall()
            elif grid[x,y] == Tiles.CORRIDOR_WALL:
                current_tile = CorridorWall()
            elif grid[x,y] == Tiles.ROOM_WALL:
                current_tile = RoomWall()
            elif grid[x,y] == Tiles.DOOR:
                current_tile = Door()
            elif grid[x,y] == Tiles.DEADEND:
                current_tile = CorridorWall()
            elif grid[x,y] == Tiles.CAVERN_FLOOR:
                current_tile = CavernFloor()
            elif grid[x,y] == Tiles.FUNGAL_CAVERN_FLOOR:
                current_tile = FungalCavernFloor()
            elif grid[x,y] == Tiles.CORRIDOR_FLOOR:
                current_tile = CorridorFloor()
            elif grid[x,y] == Tiles.ROOM_FLOOR:
                current_tile = RoomFloor()
            elif grid[x,y] == Tiles.SHALLOW_WATER:
                current_tile = ShallowWater()
            elif grid[x,y] == Tiles.DEEP_WATER:
                current_tile = DeepWater()
            elif grid[x,y] == Tiles.STAIRS_FLOOR:
                current_tile = StairsFloor()
            elif grid[x,y] == Tiles.POTENTIAL_CORRIDOR_FLOOR:
                current_tile = PotentialCorridorFloor()
            else:
                current_tile = EmptyTile()

            if (grid[x,y] in WALKABLE_TILES):
                self.make_transparent_and_walkable(x, y)

            self.grid = grid
            self.tiles[x][y] = current_tile
            self.dark_map_bg[x,y] = current_tile.out_of_fov_color
            self.light_map_bg[x,y] = current_tile.fov_color
            self.map_fg[x, y] = current_tile.foreground_color
            if current_tile.char:
                self.map_char[x,y] = ord(current_tile.char)

    def make_transparent_and_walkable(self, x, y):
        self.walkable[x, y] = True
        self.transparent[x, y] = True

    def accessible_tile(self, x, y):
        if not self.within_bounds(x,y):
            return False
        if not self.walkable[x, y]:
            return False
        return True

    def within_bounds(self, x, y, buffer=0):
        return (
            (0 + buffer <= x < self.width - buffer) and
            (0 + buffer <= y < self.height - buffer))

    def visible(self, x, y):
        return self.fov[x, y] or self.illuminated[x, y]

    def is_wall(self, x, y):
            return (not self.door[x, y]
                    and not self.transparent[x, y])

    def find_tile_within_room(self, room, tile = None):
        search_grid = np.zeros(self.walkable.shape, dtype=np.int8)

        search_grid[room.x:room.x+room.width, room.y:room.y+room.height] = room.layout

        return np.where(search_grid == tile)

    def find_random_open_position(self, base_routing_avoid=[], room = None):
        routing_avoid = base_routing_avoid.copy()
        routing_avoid.append(RoutingOptions.AVOID_BLOCKERS)
        possible_positions = self.make_walkable_array(routing_avoid)

        if room:
            search_grid = np.zeros(self.walkable.shape, dtype=np.int8)

            search_grid[room.x:room.x+room.width, room.y:room.y+room.height] = room.layout

            possible_positions[search_grid == 0] = 0

        available = np.where(possible_positions == 1)

        if (len(available) < 1):
            return None

        position = randint(0, len(available[0]) - 1)

        return Point(available[0][position], available[1][position])

    def update_and_draw_all(self, map_console, player):
        map_console.clear()

        map_console.fg[:] = self.map_fg[:]

        if self.should_shimmer > 5:
            shimmering = np.isin(self.grid, SHIMMERING_TILES)
            shimmer_list = np.where(shimmering)
            for idx, x in enumerate(shimmer_list[0]):
                y = shimmer_list[1][idx]

                self.dark_map_bg[x,y] = self.tiles[x][y].out_of_fov_shimmer
                self.light_map_bg[x,y] = self.tiles[x][y].fov_shimmer
                self.should_shimmer = 0
        else:
            self.should_shimmer += 1

        if not CONFIG.get('debug'):
            where_fov = np.where(self.fov[:])
            self.explored[where_fov] = True
            explored = np.where(self.explored[:])
        else:
            where_fov = np.where(self.light_map_bg[:])
            self.explored[:] = True
            explored = np.where(self.explored[:])

        self.map_bg[explored] = self.dark_map_bg[explored]

        dx = 0.0
        dy = 0.0
        di = 0.0

        if not CONFIG.get('debug'):
            SQUARED_TORCH_RADIUS = player.fov.fov_radius * player.fov.fov_radius

            # slightly change the perlin noise parameter
            self.torchx += 0.1
            # randomize the light position between -1.5 and 1.5
            tdx = [self.torchx + 20.0]
            dx = tcod.noise_get(self.noise, tdx, tcod.NOISE_SIMPLEX) * 1.5
            tdx[0] += 30.0
            dy = tcod.noise_get(self.noise, tdx, tcod.NOISE_SIMPLEX) * 1.5
            di = 0.2 * tcod.noise_get(
                self.noise, [self.torchx], tcod.NOISE_SIMPLEX
            )

            mgrid = np.mgrid[:self.width, :self.height]
            # get squared distance
            light = (mgrid[0] - player.x + dx) ** 2 + (
                mgrid[1] - player.y + dy
            ) ** 2
            light = light.astype(np.float16)
            visible = (light < SQUARED_TORCH_RADIUS) & self.fov[:]
            light[...] = SQUARED_TORCH_RADIUS - light
            light[...] /= SQUARED_TORCH_RADIUS
            light[...] += di
            light[...] = light.clip(0, 1)
            light[~visible] = 0

            map_console.bg[...] = (
                self.light_map_bg.astype(np.float16) - self.map_bg
            ) * light[..., np.newaxis] + self.map_bg

        else:
            map_console.bg[explored] = self.dark_map_bg[explored]
            map_console.bg[where_fov] = self.light_map_bg[where_fov]

        map_console.ch[explored] = self.map_char[explored]
        if CONFIG.get('debug'):
            for current_path in self.paths:
                for x,y in current_path:
                    map_console.bg[x,y] = COLORS.get('show_path_track')

            for current_walkable in self.walkables:
                for (x,y), value in np.ndenumerate(self.grid):
                    if (current_walkable[x, y]):
                        map_console.bg[x,y] = COLORS.get('show_walkable_path')

            self.walkables.clear()

            if CONFIG.get('show_dijkstra_player'):
                max_distance = np.amax(self.dijkstra_player)
                for (x,y), value in np.ndenumerate(self.grid):
                    map_console.ch[x, y] = ord(str(int(self.dijkstra_player[x,y] % 10)))
                    if self.dijkstra_player[x,y] != 0:
                        map_console.bg[x,y] = tcod.color_lerp(COLORS.get('dijkstra_near'), COLORS.get('dijkstra_far'), 0.9 * self.dijkstra_player[x,y] / max_distance)
            elif CONFIG.get('show_dijkstra_flee') and type(self.dijkstra_flee) is np.ndarray:
                max_distance = np.amax(self.dijkstra_flee)
                for (x,y), value in np.ndenumerate(self.grid):
                    if self.dijkstra_flee[x,y] != 0:
                        map_console.bg[x,y] = tcod.color_lerp(COLORS.get('dijkstra_near'), COLORS.get('dijkstra_far'), 0.9 * self.dijkstra_player[x,y] / max_distance)

        always_visible = self.entities.find_all_visible()
        for entity in always_visible:
            if self.explored[entity.x, entity.y]:
                map_console.ch[entity.x, entity.y] = ord(entity.display_char)
                map_console.fg[entity.x, entity.y] = entity.display_color

        auras = []
        for idx, x in enumerate(where_fov[0]):
            y = where_fov[1][idx]
            current_entities = self.entities.get_entities_in_position((x, y))
            entities_in_render_order = sorted(current_entities, key=lambda x: x.render_order.value)
            for entity in entities_in_render_order:
                if entity.invisible:
                    continue
                map_console.ch[x, y] = ord(entity.display_char)
                map_console.fg[x, y] = entity.display_color
                if entity.aura:
                    auras.append(entity)
            entities_in_render_order.clear()
            entity = None

        for entity in auras:
            slice = map_console.bg[entity.x-1:entity.x+2,entity.y-1:entity.y+2]

            for x in range(0, slice.shape[0]):
                for y in range(0, slice.shape[1]):
                    slice[x,y] = tcod.color_lerp(tcod.Color(slice[x,y][0],slice[x,y][1],slice[x,y][2]), random_color_shimmer(tcod.red), 0.05)

    def clear_paths(self):
        self.paths.clear()

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

    def update_entity_position(self, entity):
        self.blocked[entity.x, entity.y] = False
        self.transparent[entity.x, entity.y] = self.grid[entity.x, entity.y] in WALKABLE_TILES

        current_entities = self.entities.get_entities_in_position((entity.x, entity.y))

        for other_entity in current_entities:
            if other_entity.blocks:
                self.blocked[entity.x, entity.y] = True
            if not other_entity.transparent:
                self.transparent[entity.x, entity.y] = False


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
        if RoutingOptions.AVOID_FOV in routing_avoid:
            walkable = walkable * (1 - self.fov)
        #if RoutingOptions.AVOID_FIRE in routing_avoid:
        #    walkable = walkable * (1 - self.fire)
        #if RoutingOptions.AVOID_STEAM in routing_avoid:
        #    walkable = walkable * (1 - self.steam)

        mask = np.isin(self.grid, routing_avoid)

        walkable[mask] = 0

        if Tiles.STAIRS_FLOOR in routing_avoid:
            pass

        return walkable

    def walkable_for_entity_under_mouse(self, x, y):
        if self.within_bounds(x,y):
            current_entities = self.entities.get_entities_in_position((x, y))
            for entity in current_entities:
                entity_walkable = self.make_walkable_array(entity.movement.routing_avoid)
                self.walkables.append(entity_walkable)

    def find_closest_entity(self, point, range = 2, species_type = None):
        return self.entities.find_closest(point, species_type, max_distance=range)

    def find_entities_of_type(self, species_type):
        return self.entities.find_all_of_type(species_type)
