from etc.colors import COLORS
from etc.enum import ResultTypes

from game_messages import Message

from utils.random_utils import die_roll

class Usable:
    def __init__(self, name=""):
        self.name = name
        self.owner = None
        self.needs_target = False
        self.type_of_target = False

    def __str__(self):
        return f"{self.__class__} {self.name}"

    def __repr__(self):
        return f"{self.__class__} {self.name}"

    def use(self, game_map, user = None, target = None):
        results = []

        results.append({ResultTypes.MESSAGE: Message('', COLORS.get('success_text'))})

        return results

class AntidoteUsable(Usable):
    def __init__(self):
        super().__init__(name="Antidote")

    def use(self, game_map, user = None, target = None):
        results = []

        if user.poisoned:
            user.poisoned.duration = -1

        results.append({ResultTypes.DISCARD_ITEM: self.owner})
        results.append({ResultTypes.MESSAGE: Message('You feel clensed.', COLORS.get('success_text'))})

        return results

class HealingPotionUsable(Usable):
    def __init__(self, number_of_die=1, type_of_die=8):
        super().__init__(name="Healing Potion")
        self.number_of_die = number_of_die
        self.type_of_die = type_of_die

    def use(self, game_map, user = None, target = None):
        results = []

        if user.health.hp == user.health.max_hp:
            results.append({ResultTypes.MESSAGE: Message('You are already at full health', COLORS.get('success_text'))})
        else:
            user.health.heal(die_roll(self.number_of_die, self.type_of_die))
            results.append({ResultTypes.MESSAGE: Message('Your wounds start to feel better!', COLORS.get('success_text'))})
            results.append({ResultTypes.DISCARD_ITEM: self.owner})

        return results

class PowerPotionUsable(Usable):
    def __init__(self, number_of_die=1, type_of_die=8):
        super().__init__(name="Power Potion")
        self.number_of_die = number_of_die
        self.type_of_die = type_of_die

    def use(self, game_map, user = None, target = None):
        results = []

        user.offence.base_power = user.offence.base_power + die_roll(self.number_of_die, self.type_of_die)
        results.append({ResultTypes.MESSAGE: Message('You feel like you can take anything on!', COLORS.get('success_text'))})
        results.append({ResultTypes.DISCARD_ITEM: self.owner})

        return results

class DefencePotionUsable(Usable):
    def __init__(self, number_of_die=1, type_of_die=8):
        super().__init__(name="Defence Potion")
        self.number_of_die = number_of_die
        self.type_of_die = type_of_die

    def use(self, game_map, user = None, target = None):
        results = []

        user.defence.base_defence = user.defence.base_defence + die_roll(self.number_of_die, self.type_of_die)
        results.append({ResultTypes.MESSAGE: Message('You feel more secure in yourself!', COLORS.get('success_text'))})
        results.append({ResultTypes.DISCARD_ITEM: self.owner})

        return results

class ScrollUsable(Usable):
    def __init__(self, scroll_name="", scroll_spell=None, number_of_die=0, type_of_die=0):
        super().__init__(name=scroll_name)
        self.number_of_die = number_of_die
        self.scroll_spell = scroll_spell
        self.type_of_die = type_of_die

    def use(self, game_map, user = None, target = None):
        results = []

        if not target and self.needs_target:
            results.append({ResultTypes.TARGET_ITEM_IN_INVENTORY: self.owner})
        else:
            results = self.scroll_spell(game_map, user, target)
            results.append({ResultTypes.DISCARD_ITEM: self.owner})

        return results
