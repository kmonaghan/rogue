from math import sqrt
from random import randint

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

    def chebyshev_distance(self, other):
        """
        Chebyshev distance (or Tchebychev distance), maximum metric, or L∞
        metric is a metric defined on a vector space where the distance between
        two vectors is the greatest of their differences along any coordinate
        dimension.
        See: https://en.wikipedia.org/wiki/Chebyshev_distance
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return max(abs(dx), abs(dy))

    def distance_to(self, other):
        """Return the distance to another point"""
        dx = other.x - self.x
        dy = other.y - self.y
        return sqrt(dx ** 2 + dy ** 2)

    def is_neighbouring_point(self, other):
        """Check is a given point is adjacent to the current point"""
        return (abs(self.x-other.x) == 1) and (abs(self.y-other.y) == 1)

    def tuple(self):
        return (self.x, self.y)

    def random_meightbouring_point(self):
        dx = randint(-1, 1)
        dy = randint(-1, 1)

        point = Point(self.x + dx, self.y + dy)
        if (point.x < 0) or (point.y < 0):
            return self.random_meightbouring_point()

        return point
