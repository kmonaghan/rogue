from etc.enum import Tiles

class Dungeon:
    def __init__(self, width, height):
        self.height = abs(height)
        self.width = abs(width)
        self.grid = [[Tiles.EMPTY for i in range(self.height)] for i in range(self.width)]
        self.rooms = []
        self.doors = []
        self.corridors = []
        self.deadends = []
        self.alcoves = []
        self.caves = []

        self.graph = {}

    def __iter__(self):
        for xi in range(self.width):
            for yi in range(self.height):
                yield xi, yi, self.grid[xi][yi]

    def add_down_stairs(self, stairs):
        self.downward_stairs_position = None
