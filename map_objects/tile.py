__metaclass__ = type

import tcod as libtcod

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
        self.fov_color = libtcod.dark_grey
        self.out_of_fov_color = libtcod.darkest_grey
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

        self.fov_color = libtcod.lighter_sepia
        self.out_of_fov_color = libtcod.light_sepia
        self.name = "Cavern floor"

class CavernWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CavernWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia
        self.name = "Cavern wall"

class CorridorWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CorridorWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia
        self.name = "Cavern wall"

class Door(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Door, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.orange
        self.out_of_fov_color = libtcod.darker_orange
        self.name = "Door"

class ImpenetrableTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(ImpenetrableTile, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.red
        self.out_of_fov_color = libtcod.darker_red
        self.name = "Impenetrable"

class RoomFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(RoomFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.light_grey
        self.out_of_fov_color = libtcod.grey
        self.name = "Room floor"

class CorridorFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CorridorFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.sepia
        self.out_of_fov_color = libtcod.darker_sepia
        self.name = "Corridor floor"

class PotentialCorridorFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(PotentialCorridorFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.lightest_green
        self.out_of_fov_color = libtcod.lightest_green
        self.name = "Potential Corridor floor"

class RoomWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(RoomWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_grey
        self.out_of_fov_color = libtcod.darkest_grey
        self.name = "Wall"
        self.char = '#'

class StairsFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(StairsFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.light_yellow
        self.out_of_fov_color = libtcod.yellow
        self.name = "Stairs floor"

class ShallowWater(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(ShallowWater, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.lighter_blue
        self.out_of_fov_color = libtcod.light_blue
        self.name = "Shallow water"
        self.char = '~'

class DeepWater(Tile):
    def __init__(self, blocked=True, block_sight=False):
        super(DeepWater, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_blue
        self.out_of_fov_color = libtcod.darkest_blue
        self.name = "Deep water"
        self.char = '~'

class EmptyTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(EmptyTile, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.black
        self.out_of_fov_color = libtcod.black
        self.name = "An empty void that fills you with dispair as you stare into it."
