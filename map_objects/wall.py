__metaclass__ = type

import libtcodpy as libtcod

from map_objects.tile import Tile

#class Wall(Tile):
class Wall:
    """
    A Wall on a map. It may or may not be blocked, and may or may not block sight.
    """
    def __init__(self):
        self.blocked = True
        self.block_sight = True

        self.explored = False
        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

    def isFloor(self):
        return False

    def isWall(self):
        return True
