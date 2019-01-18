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

    def isFloor(self):
        return not (self.blocked and self.block_sight)

    def isWall(self):
        return (self.blocked and self.block_sight)

    def describe(self):
        return "Tile"

class CavernFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CavernFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.lighter_sepia
        self.out_of_fov_color = libtcod.light_sepia

    def describe(self):
        return "Cavern floor"

class CavernWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CavernWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

    def describe(self):
        return "Cavern wall"

class CorridorWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CorridorWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

    def describe(self):
        return "Cavern wall"

class Door(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Door, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.orange
        self.out_of_fov_color = libtcod.darker_orange

    def describe(self):
        return "Door"

class RoomFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(RoomFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.light_grey
        self.out_of_fov_color = libtcod.grey

    def describe(self):
        return "Room floor"

class CorridorFloor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(CorridorFloor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.sepia
        self.out_of_fov_color = libtcod.darker_sepia

    def describe(self):
        return "Corridor floor"

class RoomWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(RoomWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_grey
        self.out_of_fov_color = libtcod.darkest_grey

    def describe(self):
        return "Wall"

class ShallowWater(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(ShallowWater, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.lighter_blue
        self.out_of_fov_color = libtcod.light_blue

    def describe(self):
        return "Shallow water"

class DeepWater(Tile):
    def __init__(self, blocked=True, block_sight=False):
        super(DeepWater, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_blue
        self.out_of_fov_color = libtcod.darkest_blue

    def describe(self):
        return "Deep water"

class EmptyTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(EmptyTile, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.black
        self.out_of_fov_color = libtcod.black

    def describe(self):
        return "An empty void that fills you with dispair as you stare into it."
