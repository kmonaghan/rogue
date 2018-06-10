__metaclass__ = type

import libtcodpy as libtcod

import baseclasses
import game_state

from map_objects.map_utils import is_blocked
from map_objects.rect import Rect
from map_objects.point import Point

class Room(Rect):
    def __init__(self, x, y, w, h):
        super(Room, self).__init__(x,y,w,h)

        self.w = w
        self.h = h

        self.layout = None

        self.room_detail = None

        if (game_state.debug):
            name = self.describe()
            self.room_detail = baseclasses.Object(Point(self.x1, self.y1), "R", name, libtcod.red, False, True)
            game_state.objects.append(self.room_detail)

    def change_xy(self, x, y):
        self.x1 = x
        self.y1 = y
        self.x2 = x + self.w
        self.y2 = y + self.h

        if (self.room_detail != None):
            self.room_detail.x = x
            self.room_detail.y = y

    def random_tile(self):
        point = None
        while (point == None):
            x = libtcod.random_get_int(None, self.x1, self.x2)
            y = libtcod.random_get_int(None, self.y1, self.y2)

            if (is_blocked(Point(x,y)) == False):
                point = Point(x,y)

        return point

    def room_map(self, layout):
        self.w = len(layout[0])
        self.h = len(layout)

    def describe(self):
        return "Room: " + str(self.x1) + ',' + str(self.y1) + ',' + str(self.w) + ',' + str(self.h)
