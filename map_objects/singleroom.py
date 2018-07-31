import libtcodpy as libtcod

from map_objects.room import Room
from map_objects.wall import Wall
from map_objects.floor import Floor

class SingleRoom:
    def __init__(self):
        self.bsp = None
        self.DEPTH = 10
        self.MIN_SIZE = 5
        self.FULL_ROOMS = False
        self.mapWidth = 0
        self.mapHeight = 0
        self.level = []
        self.rooms = []
        self.offset = 0

    def generateLevel(self, mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset=0):
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight

        self.level = [[Wall() for y in range(mapHeight)] for x in range(mapWidth)]

        room = Room(10,10,30,30)

        #Dig room
        for x in range(10, 30):
            for y in range(10, 30):
                self.level[x][y] = Floor()

        self.rooms.append(room)

        return self.level
