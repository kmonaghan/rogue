__metaclass__ = type

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
        self.fov_color = libtcod.dark_sepia
        self.out_of_fov_color = libtcod.darkest_sepia

    def setWall(self):
        self.blocked = True
        self.block_sight = True

    def setFloor(self):
        self.blocked = False
        self.block_sight = False

    def isFloor(self):
        return not (self.blocked and self.block_sight)

    def isWall(self):
        return (self.blocked and self.block_sight)
