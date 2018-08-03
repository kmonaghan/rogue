import libtcodpy as libtcod

from map_objects.floor import Floor
from map_objects.room import Room
from map_objects.point import Point
from map_objects.wall import Wall

class LevelMap:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.offset = 0

        self.level = []
        self.rooms = []

        self.ROOM_MIN_SIZE = 16 # size in total number of cells, not dimensions
        self.ROOM_MAX_SIZE = 500 # size in total number of cells, not dimensions

    def generateLevel(self, mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset):
        self.width = mapWidth
        self.height = mapHeight

        self.ROOM_MIN_SIZE = room_min_size
        self.ROOM_MAX_SIZE = room_max_size

        self.offset = offset
        
        self.level = [[Wall() for y in range(self.height)]
                    for x in range(self.width)]

        return self.level
