import libtcodpy as libtcod

from map_objects.levelmap import LevelMap
from map_objects.altbsptree import AltBSPTree
from map_objects.cellularautomata import CellularAutomata

class Mixed(LevelMap):
    def __init__(self):
        super(Mixed, self).__init__()
        self.caves = []

    def generateLevel(self, mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset):
        super(Mixed, self).generateLevel(mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset)

        print("mixed mapWidth: " + str(mapWidth))

        third = int(self.width / 3)

        print("1/3 " + str(third))

        mines = AltBSPTree()
        mines.generateLevel(third, self.height, max_rooms, room_min_size, room_max_size, offset)

        for x in range(0, third):
            for y in range(0, self.height):
                self.level[x][y] = mines.level[x][y]

        self.rooms = mines.rooms

        cavern = CellularAutomata()
        cavern.generateLevel(self.width - third, self.height, max_rooms, room_min_size, room_max_size, offset)

        for x in range(third, self.width):
            for y in range(0, self.height):
                self.level[x][y] = cavern.level[x - third][y]

        for room in cavern.rooms:
            room.change_xy(room.x1 + third, room.y1)
            self.caves.append(room)

        return self.level
