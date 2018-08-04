import libtcodpy as libtcod

from random import randint

from map_objects.levelmap import LevelMap
from map_objects.altbsptree import AltBSPTree
from map_objects.cellularautomata import CellularAutomata

from map_objects.floor import Floor
from map_objects.point import Point
from map_objects.room import Room
from map_objects.wall import Wall

class Mixed(LevelMap):
    def __init__(self):
        super(Mixed, self).__init__()
        self.caves = []

    def generateLevel(self, mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset):
        super(Mixed, self).generateLevel(mapWidth, mapHeight, max_rooms, room_min_size, room_max_size, offset)

        third = int(self.width / 3)

        y = randint(1, self.height - 10)
        entrance = Room(0, y, 5, 5)

        mines = AltBSPTree()
        mines.generateLevel(third, self.height, max_rooms, room_min_size, room_max_size, offset)

        cavern = CellularAutomata()
        cavern.generateLevel(self.width - third, self.height, max_rooms, room_min_size, room_max_size, offset)

        for x in range(self.width - third, self.width):
            for y in range(0, self.height):
                self.level[x][y] = mines.level[x - (self.width - third)][y]

        for room in mines.rooms:
            room.change_xy(room.x1 + (self.width - third), room.y1)
            self.rooms.append(room)

        for x in range((entrance.w + 1), self.width - third):
            for y in range(0, self.height):
                self.level[x][y] = cavern.level[x - (entrance.w + 1)][y]

        for room in cavern.rooms:
            room.change_xy(room.x1 + third, room.y1)
            self.caves.append(room)

        self.linkMaps()

        self.rooms = [entrance] + self.rooms
        self.digRoom(entrance)

        x = self.width

        closest_cave = None

        for room in self.caves:
            if (room.x1 < x):
                closest_cave = room
                x = room.x1

        if (closest_cave):
            self.createHall(entrance, closest_cave)

        return self.level

    def linkMaps(self):
        target_x = int(self.width / 3)

        x = self.width

        closest_room = None
        closest_cave = None

        for room in self.rooms:
            if (room.x1 < x):
                closest_room = room
                x = room.x1

        x = 0

        for room in self.caves:
            if ((room.x1 + room.w) > x):
                closest_cave = room
                x = (room.x1 + room.w)

        if (closest_room and closest_cave):
            self.createHall(closest_room, closest_cave)

    def createHall(self, room1, room2):
        # connect two rooms by hallways
        point1 = room1.center()
        point2 = room2.center()

        #print "Room centers " + point1.describe() + ' and ' + point2.describe()

        # 50% chance that a tunnel will start horizontally
        if randint(0,1) == 1:
            self.createHorTunnel(point1.x, point2.x, point1.y)
            self.createVirTunnel(point1.y, point2.y, point2.x)

        else: # else it starts virtically
            self.createVirTunnel(point1.y, point2.y, point1.x)
            self.createHorTunnel(point1.x, point2.x, point2.y)

    def createHorTunnel(self, x1, x2, y):
        for x in range(min(x1,x2),max(x1,x2)+1):
            self.level[x][y] = Floor()
            self.level[x][y].fov_color = libtcod.red

    def createVirTunnel(self, y1, y2, x):
        for y in range(min(y1,y2),max(y1,y2)+1):
            self.level[x][y] = Floor()
            self.level[x][y].fov_color = libtcod.red
