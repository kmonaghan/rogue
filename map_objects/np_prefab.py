import numpy as np
from random import randint

from etc.enum import Tiles

class Prefab:
    def __init__(self, room_map, randomly_rotate=True, top=1, middle=1, bottom=1):
        room_layout = room_map(top, middle, bottom)
        self.layout = np.zeros((len(room_layout), len(room_layout[0])), dtype=np.int8)
        self.randomly_rotate = randomly_rotate
        self.name = room_map.__name__
        self.exits = []
        self.spawnpoints = []

        self.parse_map(room_layout)

    def parse_map(self, room_layout):
        for x in range(0, len(room_layout)):
            for y  in range(0, len(room_layout[0])):
                if (room_layout[x][y] == "#"):
                    self.layout[x, y] = Tiles.ROOM_WALL
                elif (room_layout[x][y] == "I"):
                    self.layout[x, y] = Tiles.IMPENETRABLE
                elif (room_layout[x][y] == "E"):
                    self.layout[x, y] = Tiles.EXIT_DOOR
                elif (room_layout[x][y] == "W"):
                    self.layout[x, y] = Tiles.SHALLOW_WATER
                elif (room_layout[x][y] == "X"):
                    self.layout[x, y] = Tiles.STAIRS_FLOOR
                elif (room_layout[x][y] == "D"):
                    self.layout[x, y] = Tiles.DOOR
                elif (room_layout[x][y] == "V"):
                    self.layout[x, y] = Tiles.EMPTY
                elif (room_layout[x][y] == "."):
                    self.layout[x, y] = Tiles.ROOM_FLOOR
                elif (room_layout[x][y] == "S"):
                    self.layout[x, y] = Tiles.SPAWN_POINT

        if self.randomly_rotate:
            rotations = randint(0, 3)

            if rotations > 0:
                self.layout = np.rot90(self.layout, rotations)

        tiles = np.where(self.layout == Tiles.SPAWN_POINT)
        self.spawnpoints = list(zip(tiles[0],tiles[1]))

        self.layout[np.where(self.layout == Tiles.SPAWN_POINT)] = Tiles.ROOM_FLOOR

        tiles = np.where(self.layout == Tiles.EXIT_DOOR)
        self.exits = list(zip(tiles[0],tiles[1]))

        self.layout[np.where(self.layout == Tiles.EXIT_DOOR)] = Tiles.DOOR
