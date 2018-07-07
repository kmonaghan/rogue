__metaclass__ = type

import libtcodpy as libtcod

from map_objects.tile import Tile

#class Floor(Tile):
#    def __init__(self, blocked=False, block_sight=False):
#        super(Tile, self).__init__()
#
#        self.fov_color = libtcod.sepia
#        self.out_of_color = libtcod.darker_sepia
class Floor:
    """
    A Floor on a map. It may or may not be blocked, and may or may not block sight.
    """
    def __init__(self):
        self.blocked = False
        self.block_sight = False

        self.explored = False
        self.fov_color = libtcod.sepia
        self.out_of_fov_color = libtcod.darker_sepia

    def isFloor(self):
        return True

    def isWall(self):
        return False
