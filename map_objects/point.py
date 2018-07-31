class Point:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def describe(self):
        return str(self.x) + ', ' + str(self.y)

    def distance_to(self, other):
        #return the distance to another point
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
