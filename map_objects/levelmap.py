import libtcodpy as libtcod

from map_objects.floor import Floor
from map_objects.room import Room
from map_objects.point import Point
from map_objects.wall import Wall

class LevelMap:
    def __init__(self):
        self.resetMap()

    def generateLevel(self, mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset):
        self.width = mapWidth
        self.height = mapHeight

        self.ROOM_MIN_SIZE = room_min_size
        self.ROOM_MAX_SIZE = room_max_size

        self.offset = offset

        self.level = [[Wall() for y in range(self.height)]
                    for x in range(self.width)]

        return self.level

    def digRoom(self, room):
        minx = room.x1
        maxx = room.x1 + room.w + 1

        miny = room.y1
        maxy = room.y1 + room.h + 1

        for x in range(minx, maxx):
            for y in range(miny, maxy):
                self.level[x][y] = Floor()

    def checkAvailablePath(self, start, target):
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(self.width, self.height)

        for y1 in range(self.height):
            for x1 in range(self.width):
                libtcod.map_set_properties(fov, x1, y1, not self.level[x1][y1].block_sight,
                                           not self.level[x1][y1].blocked)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        #my_path = libtcod.path_new_using_map(fov, 1.41)
        my_path = libtcod.path_new_using_map(fov, 0.0)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, start.x, start.y, target.x, target.y)

        has_path = not libtcod.path_is_empty(my_path)

        libtcod.path_delete(my_path)

        return has_path

    def resetMap(self):
        self.width = 0
        self.height = 0

        self.offset = 0

        self.level = []
        self.rooms = []

        self.ROOM_MIN_SIZE = 16 # size in total number of cells, not dimensions
        self.ROOM_MAX_SIZE = 500 # size in total number of cells, not dimensions

    def getAdjacentWallsSimple(self, x, y): # finds the walls in four directions
        wallCounter = 0
        #print("(",x,",",y,") = ",self.level[x][y])
        if (self.level[x][y-1].isWall()): # Check north
            wallCounter += 1
        if (self.level[x][y+1].isWall()): # Check south
            wallCounter += 1
        if (self.level[x-1][y].isWall()): # Check west
            wallCounter += 1
        if (self.level[x+1][y].isWall()): # Check east
            wallCounter += 1

        return wallCounter

    def getAdjacentWalls(self, tileX, tileY): # finds the walls in 8 directions
        wallCounter = 0
        for x in range (tileX-1, tileX+2):
            for y in range (tileY-1, tileY+2):
                if (self.level[x][y].isWall()):
                    if (x != tileX) or (y != tileY): # exclude (tileX,tileY)
                        wallCounter += 1
        return wallCounter
