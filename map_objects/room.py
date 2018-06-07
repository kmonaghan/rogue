__metaclass__ = type

import libtcodpy as libtcod

from map_objects.map_utils import is_blocked
from map_objects.rect import Rect
from map_objects.point import Point

class Room(Rect):
    def __init__(self, minx, miny, maxx, maxy):
        super(Room, self).__init__(minx,miny,maxx-minx,maxy-miny)
        self.w = maxx-minx + 1
        self.h = maxy-miny + 1

            #Dig room
#            for x in range(minx, maxx + 1):
#                for y in range(miny, maxy + 1):
#                    map[x][y].blocked = False
#                    map[x][y].block_sight = False

    def random_tile(self):
        point = None
        while (point == None):
            x = libtcod.random_get_int(None, self.x1 + 1, self.w - 2)
            y = libtcod.random_get_int(None, self.y1 + 1, self.h - 2)

            #if (is_blocked(Point(x,y)) == False):
            point = Point(x,y)

        return point
