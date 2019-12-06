from random import randint

from etc.colors import COLORS

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
            self.subcolor = COLORS.get('species_fiery')
            self.bonus_power = 1
        elif (dice <= 20):
            self.name = "Icy"
            self.subcolor = COLORS.get('species_icy')
            self.bonus_defence = 1
        elif (dice <= 30):
            self.name = "Brass"
            self.subcolor = COLORS.get('species_brass')
        elif (dice <= 40):
            self.name = "Copper"
            self.subcolor = COLORS.get('species_copper')
        else:
            self.name = "Golden"
            self.subcolor = COLORS.get('species_golden')
