from random import randint

class Shimmer:
    def __init__(self, alt_color = True, alt_char = None, alt_chance = 100):
        self.owner = None
        self.alt_char = alt_char
        self.alt_color = alt_color
        self.alt_chance = alt_chance

    @property
    def display_char(self):
        if randint(1,100) >= self.alt_chance:
            return self.alt_char

        return self.owner.char

    @property
    def display_color(self):
        if self.alt_color:
            return random_color_shimmer(self.color)

        return self.owner.color
