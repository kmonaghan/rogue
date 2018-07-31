__metaclass__ = type

import libtcodpy as libtcod

from map_objects.tile import Tile

class Wall(Tile):
    """
    A Wall on a map. It may or may not be blocked, and may or may not block sight.
    """
    def __init__(self, blocked=True, block_sight=True):
        super(Wall, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

    def isFloor(self):
        return False

    def isWall(self):
        return True
