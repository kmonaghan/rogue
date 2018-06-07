__metaclass__ = type

import libtcodpy as libtcod

import baseclasses
import game_state

from map_objects.map_utils import is_blocked
from map_objects.rect import Rect
from map_objects.point import Point

class Room(Rect):
    def __init__(self, minx, miny, maxx, maxy):
        super(Room, self).__init__(minx,miny,maxx-minx,maxy-miny)

        self.w = maxx-minx + 1
        self.h = maxy-miny + 1

        if game_state.debug:
            name = str(self.x1) + ', ' + str(self.y1) + ', ' + str(self.w) + ', ' + str(self.h)
            print name
            room_detail = baseclasses.Object(Point(self.x1, self.y1), "R", name, libtcod.red, True, True)
            game_state.objects.append(room_detail)

    def random_tile(self):
        point = None
        while (point == None):
            x = libtcod.random_get_int(None, self.x1 + 1, self.w - 2)
            y = libtcod.random_get_int(None, self.y1 + 1, self.h - 2)

            if (is_blocked(Point(x,y)) == False):
                point = Point(x,y)

        return point
