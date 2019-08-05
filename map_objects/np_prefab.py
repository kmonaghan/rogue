import numpy as np
from random import randint

from etc.enum import Tiles

class Prefab:
    def __init__(self, room_map, randomly_rotate=True):
        self.layout = np.zeros((len(room_map), len(room_map[0])), dtype=np.int8)
        self.randomly_rotate = randomly_rotate

        self.parse_map(room_map)

    def parse_map(self, room_map):
        for x in range(0, len(room_map)):
            for y  in range(0, len(room_map[0])):
                if (room_map[x][y] == "#"):
                    self.layout[x, y] = Tiles.ROOM_WALL
                elif (room_map[x][y] == "I"):
                    self.layout[x, y] = Tiles.IMPENETRABLE
                elif (room_map[x][y] == "E"):
                    self.layout[x, y] = Tiles.EMPTY
                elif (room_map[x][y] == "W"):
                    self.layout[x, y] = Tiles.SHALLOWWATER
                elif (room_map[x][y] == "S"):
                    self.layout[x, y] = Tiles.STAIRSFLOOR
                elif (room_map[x][y] == "D"):
                    self.layout[x, y] = Tiles.DOOR
                elif (room_map[x][y] == "V"):
                    self.layout[x, y] = Tiles.EMPTY
                elif (room_map[x][y] == "."):
                    self.layout[x, y] = Tiles.ROOM_FLOOR

        if self.randomly_rotate:
            rotations = randint(0, 3)

            if rotations > 0:
                self.layout = np.rot90(self.layout, rotations)
