class Point:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def describe(self):
        return str(self.x) + ', ' + str(self.y)
