__metaclass__ = type

from etc.colors import COLORS, random_light_shallow_water, random_dark_shallow_water, random_light_deep_water, random_dark_deep_water

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

        self.explored = False
        self.fov_color = COLORS.get('light_default')
        self.out_of_fov_color = COLORS.get('dark_default')
        self.name = "Tile"
        self.char = None

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"

    def isFloor(self):
        return not (self.blocked and self.block_sight)

    def isWall(self):
        return (self.blocked and self.block_sight)

class CavernFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CavernFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_floor')
        self.out_of_fov_color = COLORS.get('light_cavern_floor')
        self.name = "Cavern floor"

class CavernWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CavernWall, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_wall')
        self.out_of_fov_color = COLORS.get('dark_cavern_wall')
        self.name = "Cavern wall"

class CorridorWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CorridorWall, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_cavern_wall')
        self.out_of_fov_color = COLORS.get('dark_cavern_wall')
        self.name = "Cavern wall"

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

class CorridorFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CorridorFloor, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_corridor_floor')
        self.out_of_fov_color = COLORS.get('dark_corridor_floor')
        self.name = "Corridor floor"

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
        self.out_of_fov_color = COLORS.get('dark_corridor_floor')
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
        self.char = '~'

    @property
    def fov_shimmer(self):
        return random_light_shallow_water()

    @property
    def out_of_fov_shimmer(self):
        return random_dark_shallow_water()

class DeepWater(Tile):
    def __init__(self, blocked=True, block_sight=False):
        super(DeepWater, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_deep_water')
        self.out_of_fov_color = COLORS.get('dark_deep_water')
        self.name = "Deep water"
        self.char = '~'

    @property
    def fov_shimmer(self):
        return random_light_deep_water()

    @property
    def out_of_fov_shimmer(self):
        return random_dark_deep_water()

class EmptyTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(EmptyTile, self).__init__(blocked, block_sight)

        self.fov_color = COLORS.get('light_empty_tile')
        self.out_of_fov_color = COLORS.get('dark_empty_tile')
        self.name = "An empty void that fills you with dispair as you stare into it."
