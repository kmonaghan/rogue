from math import sqrt
class Point:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Point):
            return ((self.x == other.x) and (self.y == other.y))

        return NotImplemented

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __repr__(self):
        return f"{self.x}, {self.y}"

    def distance_to(self, other):
        #return the distance to another point
        dx = other.x - self.x
        dy = other.y - self.y
        return sqrt(dx ** 2 + dy ** 2)

    def random_meightbouring_point(self):
        dx = libtcod.random_get_int(0, -1, 1)
        dy = libtcod.random_get_int(0, -1, 1)

        point = Point(self.x + dx, self.y + dy)
        if (point.x < 0) or (point.y < 0):
            return self.random_meightbouring_point()

        return point
