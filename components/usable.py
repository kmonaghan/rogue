import tcod as libtcod

from etc.enum import ResultTypes

from game_messages import Message

from utils.random_utils import die_roll

class Usable:
    def __init__(self, name=""):
        self.name = ""
        self.owner = None

    def __str__(self):
        return f"{self.__class__} {self.name}"

    def __repr__(self):
        return f"{self.__class__} {self.name}"

    def use(self, game_map, target = None):
        return []

class HealingPotionUsable(Usable):
    def __init__(self, number_of_die=1, type_of_die=8):
        super().__init__(name="Healing Potion")
        self.number_of_die = number_of_die
        self.type_of_die = type_of_die

    def use(self, game_map, target = None):
        results = []

        if target.health.hp == target.health.max_hp:
            results.append({ResultTypes.MESSAGE: Message('You are already at full health', libtcod.yellow)})
        else:
            target.health.heal(die_roll(self.number_of_die, self.type_of_die))
            results.append({ResultTypes.MESSAGE: Message('Your wounds start to feel better!', libtcod.green)})
            results.append({ResultTypes.DISCARD_ITEM: self.owner})

        return results
