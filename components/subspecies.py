import libtcodpy as libtcod

class Subspecies:
    def __init__(self):
        self.name = None
        self.subcolor = None

    def random_subspecies(self):
        dice = libtcod.random_get_int(0, 1, 100)
        if (dice <= 10):
            self.name = "Fiery"
            self.subcolor = libtcod.red
        elif (dice <= 20):
            self.name = "Icy"
            self.subcolor = libtcod.blue
        elif (dice <= 30):
            self.name = "Brass"
            self.subcolor = libtcod.brass
        elif (dice <= 40):
            self.name = "Copper"
            self.subcolor = libtcod.copper
        else:
            self.name = "Golden"
            self.subcolor = libtcod.gold
