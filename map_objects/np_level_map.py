import numpy as np
import time

from random import randint

import tcod

from tcod.console import Console
from tcod.map import Map

from entities.entity_list import EntityList

from etc.colors import COLORS, random_color_shimmer
from etc.configuration import CONFIG
from etc.enum import RoutingOptions, Tiles, WALKABLE_TILES

from map_objects.point import Point
from map_objects.tile import (CavernFloor, CavernWall, CorridorFloor,
                                CorridorWall, DeepWater, Door, FungalCavernFloor,
                                ImpenetrableTile, RoomFloor, RoomWall,
                                ShallowWater, StairsFloor, EmptyTile,
                                PotentialCorridorFloor, SHROUD, EMPTY)

from utils.utils import matprint

class LevelMap(Map):
    def __init__(self, grid, rooms = []):
        width, height = grid.shape
        super().__init__(width, height, order="F")
        self.entities = EntityList(width, height)
        # TODO: Add to docstring

        # These need to be int8's to work with the tcod pathfinder
        self.grid = np.zeros(self.walkable.shape, dtype=np.int8)
        self.explored = np.full(
            self.walkable.shape, fill_value=False, order="F"
        )
        self.blocked = np.zeros(self.walkable.shape, dtype=np.int8)
        self.npc_fov = self.fov

        self.dungeon_level = 1

        self.tiles = np.full((width, height), fill_value=EMPTY, order="F")

        self.blit_floor(grid)

        self.paths = []

        self.noise = tcod.noise.Noise(1)  # 1D noise for the torch flickering.

        self.rooms = rooms

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

            self.tiles[x,y] = current_tile.glyph

    def make_transparent_and_walkable(self, x, y):
        self.walkable[x, y] = True
        self.transparent[x, y] = True

    def accessible_tile(self, x, y):
        if not self.within_bounds(x,y):
            return False
        if not self.walkable[x, y]:
            return False
        return True

    def within_bounds(self, x, y):
        return (
            (0 <= x < self.width) and
            (0 <= y < self.height))

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

    def render(self, console: Console) -> None:
        """
        Renders the map.
        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.tiles_rgb[:] = np.select(
            condlist=[self.fov, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=SHROUD
        )

        if not CONFIG.get('debug'):
            where_fov = np.where(self.fov[:])
        else:
            where_fov = np.where(self.tiles[:])
            self.render_debug(console)

        always_visible = self.entities.find_all_visible()
        for entity in always_visible:
            if self.explored[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.display_char, fg=entity.display_color)

        for idx, x in enumerate(where_fov[0]):
            y = where_fov[1][idx]
            current_entities = self.entities.get_entities_in_position((x, y))
            entities_in_render_order = sorted(current_entities, key=lambda x: x.render_order.value, reverse=True)
            for entity in entities_in_render_order:
                if not entity.invisible:
                    console.print(entity.x, entity.y, entity.display_char, fg=entity.display_color)
                    break
            entities_in_render_order.clear()
            entity = None

    def render_torch(self, x, y, fov_radius, console: Console) -> None:
        SQUARED_TORCH_RADIUS = fov_radius * fov_radius

        # Derive the touch from noise based on the current time.
        torch_t = time.perf_counter() * 5
        # Randomize the light position between -1.5 and 1.5
        torch_x = x + self.noise.get_point(torch_t) * 1.5
        torch_y = y + self.noise.get_point(torch_t + 11) * 1.5
        # Extra light brightness.
        brightness = 0.2 * self.noise.get_point(torch_t + 17)

        # Get the squared distance using a mesh grid.
        x, y = np.mgrid[:self.width, :self.height]
        # Center the mesh grid on the torch position.
        x = x.astype(np.float32) - torch_x
        y = y.astype(np.float32) - torch_y

        distance_squared = x ** 2 + y ** 2  # 2D squared distance array.

        # Get the currently visible cells.
        visible = (distance_squared < SQUARED_TORCH_RADIUS) & self.fov

        # Invert the values, so that the center is the 'brightest' point.
        light = SQUARED_TORCH_RADIUS - distance_squared
        light /= SQUARED_TORCH_RADIUS  # Convert into non-squared distance.
        light += brightness  # Add random brightness.
        light.clip(0, 1, out=light)  # Clamp values in-place.
        light[~visible] = 0  # Set non-visible areas to darkness.

        # Setup background colors for floating point math.
        light_bg = self.tiles["light"]["bg"].astype(np.float16)
        #dark_bg = self.tiles["dark"]["bg"].astype(np.float16)
        light_bg[~self.explored] = 0
        #dark_bg[~self.explored] = 0

        # Linear interpolation between colors.
        console.tiles_rgb["bg"] = (
            #dark_bg + (light_bg - dark_bg) * light[..., np.newaxis]
            light_bg * light[..., np.newaxis]

        )

    def render_debug(self, console: Console) -> None:
        for current_path in self.paths:
            for x,y in current_path:
                console.bg[x,y] = COLORS.get('show_path_track')

    def render_dijkstra(self, dijkstra, console: Console) -> None:
        dijkstra = np.where(dijkstra==np.iinfo(np.int32).max, -1, dijkstra)
        max_distance = np.amax(dijkstra)
        for (x,y), value in np.ndenumerate(self.grid):
            if dijkstra[x,y] > 0:
                console.bg[x,y] = tcod.color_lerp(COLORS.get('dijkstra_near'), COLORS.get('dijkstra_far'), 0.9 * dijkstra[x,y] / max_distance)

    def render_entity_detail(self, highlighted_path, target, console: Console) -> None:
        if highlighted_path:
            for x,y in highlighted_path:
                console.bg[x,y] = COLORS.get('show_entity_track')
        if target:
            console.bg[target.x,target.y] = tcod.black

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

        mask = np.isin(self.grid, routing_avoid)

        walkable[mask] = 0

        return walkable

    def find_closest_entity(self, point, species = None, radius = 2):
        """Find all the closest entity of a species to a given point within a
        given radius.

        Parameters
        ----------
        point: Point
            Center point of the search
        species: etc.enum.Species
            Species that this entity will attempt to find.
        radius: int
            The radius to search within.

        Returns
        -------
        Entity or None
          A valid entity or None if none found.
        """
        return self.entities.find_closest(point, species, radius)

    def find_entities_in_radius(self, point, species = None, radius = 2):
        """Find all the closest entities of a species to a given point within a
        given radius.

        Parameters
        ----------
        point: Point
            Center point of the search
        species: etc.enum.Species
            Species that this entity will attempt to find.
        radius: int
            The radius to search within.

        Returns
        -------
        npcs: [Entities]
          A list of all valid entities.
        """
        return self.entities.find_all_closest(point, species, radius)

    def find_entities_of_type(self, species_type):
        return self.entities.find_all_of_type(species_type)
