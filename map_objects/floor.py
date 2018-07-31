__metaclass__ = type

import libtcodpy as libtcod

from map_objects.tile import Tile

class Floor(Tile):
    """
    A Floor on a map. It may or may not be blocked, and may or may not block sight.
    """

    def __init__(self, blocked=False, block_sight=False):
        super(Floor, self).__init__(blocked, block_sight)

        self.fov_color = libtcod.sepia
        self.out_of_fov_color = libtcod.darker_sepia

    def isFloor(self):
        return True

    def isWall(self):
        return False
