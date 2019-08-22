from random import randint

import tcod as libtcod

class Subspecies:
    def __init__(self):
        self.name = None
        self.subcolor = None
        self.bonus_power = 0
        self.bonus_defence = 0

    def random_subspecies(self):
        dice = randint(1, 100)
        if (dice <= 10):
            self.name = "Fiery"
            self.subcolor = libtcod.red
            self.bonus_power = 1
        elif (dice <= 20):
            self.name = "Icy"
            self.subcolor = libtcod.blue
            self.bonus_defence = 1
        elif (dice <= 30):
            self.name = "Brass"
            self.subcolor = libtcod.brass
        elif (dice <= 40):
            self.name = "Copper"
            self.subcolor = libtcod.copper
        else:
            self.name = "Golden"
            self.subcolor = libtcod.gold
