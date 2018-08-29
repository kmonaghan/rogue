__metaclass__ = type

import libtcodpy as libtcod

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

class Cave(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Cave, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.lighter_sepia
        self.out_of_fov_color = libtcod.light_sepia

class CaveWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CaveWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

class CorridorWall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(CorridorWall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

class Door(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Door, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.orange
        self.out_of_fov_color = libtcod.darker_orange

class Floor(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Floor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.light_grey
        self.out_of_fov_color = libtcod.grey

class Ground(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(Ground, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.sepia
        self.out_of_fov_color = libtcod.darker_sepia

class Wall(Tile):
    def __init__(self, blocked=True, block_sight=True):
        super(Wall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_grey
        self.out_of_fov_color = libtcod.darkest_grey

class ShallowWater(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(ShallowWater, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.lighter_blue
        self.out_of_fov_color = libtcod.light_blue

class DeepWater(Tile):
    def __init__(self, blocked=True, block_sight=False):
        super(DeepWater, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_blue
        self.out_of_fov_color = libtcod.darkest_blue

class EmptyTile(Tile):
    def __init__(self, blocked=False, block_sight=False):
        super(EmptyTile, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.black
        self.out_of_fov_color = libtcod.black
