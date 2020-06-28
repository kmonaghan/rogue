from random import choice
from typing import Tuple

import numpy as np

from etc.colors import COLORS, random_color_shimmer

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("name", "<U50"),  # Name of the tile to be displayed.
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)

def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    name: str,
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((name, walkable, transparent, dark, light), dtype=tile_dt)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)
EMPTY = new_tile(
    name="Nothingness",
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (0, 0, 0)),
    light=(ord(" "), (255, 255, 255), (0, 0, 0)),
)

class Tile:
    """
    A tile on a map. It may or may not be blocked, and may or may not block sight.
    """
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight
        self.walkable = not self.blocked
        self.explored = False
        self.fov_color = COLORS.get('light_default')
        self.out_of_fov_color = COLORS.get('dark_default')
        self.foreground_color = COLORS.get('foreground_default')
        self.name = "Tile"
        self.char = " "
        self._glyph = None

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"

    @property
    def glyph(self):
        if not self._glyph:
            self._glyph = new_tile(
                name=np.string_(self.name),
                walkable=self.walkable,
                transparent=self.block_sight,
                dark=(ord(self.char), self.foreground_color, self.out_of_fov_color),
                light=(ord(self.char), self.foreground_color, self.fov_color),
            )

        return self._glyph

class CavernFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CavernFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_floor')
        self.out_of_fov_color = COLORS.get('dark_cavern_floor')
        self.name = "Cavern floor"
        self.char = choice([',','`',';',"'"])

class FungalCavernFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(FungalCavernFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_floor')
        self.out_of_fov_color = COLORS.get('dark_cavern_floor')
        self.foreground_color = COLORS.get('light_fungal_cavern_floor')
        self.name = "Fungus covered cavern floor"
        self.char = '"'

class CavernWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CavernWall, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_wall')
        self.out_of_fov_color = COLORS.get('dark_cavern_wall')
        self.name = "Cavern wall"
        self.char = '#'

class CorridorWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CorridorWall, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_wall')
        self.out_of_fov_color = COLORS.get('dark_cavern_wall')
        self.name = "Corridor wall"
        self.char = '#'

class Door(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Door, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_door_tile')
        self.out_of_fov_color = COLORS.get('dark_door_tile')
        self.name = "Room Floor"

class InternalDoor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(InternalDoor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_door_tile')
        self.out_of_fov_color = COLORS.get('dark_door_tile')
        self.name = "Room Floor"
        self.char = '.'

class ImpenetrableTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(ImpenetrableTile, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_impenetrable')
        self.out_of_fov_color = COLORS.get('dark_impenetrable')
        self.name = "Impenetrable"

class RoomFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(RoomFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_room_floor')
        self.out_of_fov_color = COLORS.get('dark_room_floor')
        self.name = "Room floor"
        self.char = '.'

class CorridorFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CorridorFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_room_floor')
        self.out_of_fov_color = COLORS.get('dark_room_floor')
        self.name = "Corridor floor"
        self.char = '.'

class PotentialCorridorFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(PotentialCorridorFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_potential_corridor_floor')
        self.out_of_fov_color = COLORS.get('dark_potential_corridor_floor')
        self.name = "Potential Corridor floor"

class RoomWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(RoomWall, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_room_wall')
        self.out_of_fov_color = COLORS.get('dark_room_wall')
        self.name = "Wall"
        self.char = '#'

class StairsFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(StairsFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_stair_floor')
        self.out_of_fov_color = COLORS.get('dark_stair_floor')
        self.name = "Stairs floor"

class ShallowWater(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(ShallowWater, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_shallow_water')
        self.out_of_fov_color = COLORS.get('dark_shallow_water')
        self.name = "Shallow water"
        self.char = chr(247)

class DeepWater(Tile):
    def __init__(self, blocked=True, block_sight=False):
        super(DeepWater, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_deep_water')
        self.out_of_fov_color = COLORS.get('dark_deep_water')
        self.name = "Deep water"
        self.char = chr(247)

class EmptyTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(EmptyTile, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_empty_tile')
        self.out_of_fov_color = COLORS.get('dark_empty_tile')
        self.name = "An empty void that fills you with dispair as you stare into it."
