from random import randint
from components.poisoned import Poisoned

class Poisoner:
    def __init__(self, chance_to_posion=50, damage_per_turn=1, duration=1):
        self.owner = None
        self.chance_to_posion = chance_to_posion
        self.damage_per_turn = damage_per_turn
        self.duration = duration

    def attacked_target(self, target):
        if randint(1, 100) > self.chance_to_posion:
            poison = Poisoned(self.damage_per_turn, self.duration)
            target.add_component(poison, 'poisoned')
            poison.start()
