from random import randint

from etc.colors import COLORS
from etc.enum import ResultTypes

from game_messages import Message

from utils.random_utils import die_roll

class Ablity:
    def __init__(self, name = ""):
        self.owner = None
        self.name = name

    def __str__(self):
        return f"{self.__class__} {self.name}"

    def __repr__(self):
        return f"{self.__class__} {self.name}"

    def on_attack(self, source, target):
        pass

    def on_defend(self, source, target):
        pass

class PushBack(Ablity):
    def __init__(self, distance=3, damage=10, chance=75):
        super().__init__(name="PushBack")
        self.distance = distance
        self.damage = damage
        self.chance = chance

    def on_attack(self, source, target):
        results = []

        dice = randint(1,100)
        if dice < self.chance:
            return results

        spaces = randint(1,self.distance)
        dx = target.x - source.x
        dy = target.y - source.y

        for i in range(spaces):
            results.extend([{ResultTypes.MOVE_FORCE: (target, dx, dy, self.damage)}])

        return results

class Shocking(Ablity):
    def __init__(self, number_of_dice=1, type_of_dice=6):
        super().__init__(name="Shock")
        self.number_of_dice = number_of_dice
        self.type_of_dice = type_of_dice

    def on_attack(self, source, target):
        results = []

        damage = die_roll(self.number_of_dice, self.type_of_dice)

        msg_text = '{0} takes {1} shock damage.'
        msg = Message(msg_text.format(target.name, str(damage)), COLORS.get('damage_text'))
        results.extend(target.health.take_damage(damage, source))
        results.extend([{ResultTypes.MESSAGE: msg}])

        return results
