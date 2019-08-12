import tcod as libtcod

from etc.enum import ResultTypes

from game_messages import Message

from utils.random_utils import die_roll

class Consumable:
    def __init__(self, charges=0, discard = True):
        self.charges = charges
        self.discard = discard
        self.owner = None

    def __str__(self):
        return f"Charges: {self.charges}"

    def consume(self):
        self.charges = max(0, self.charges-1)
