from etc.colors import COLORS
from etc.enum import ResultTypes

from game_messages import Message

from utils.random_utils import die_roll

class Usable:
    def __init__(self, name=""):
        self.name = name
        self.owner = None
        self.needs_target = False
        self.targeting_message = None

    def __str__(self):
        return f"{self.__class__} {self.name}"

    def __repr__(self):
        return f"{self.__class__} {self.name}"

    def use(self, game_map, user = None, target = None):
        results = []

        return results

class PotionUsable(Usable):
    def __init__(self, name="", spell=None, number_of_die=0, type_of_die=0):
        super().__init__(name=name)
        self.number_of_die = number_of_die
        self.spell = spell
        self.type_of_die = type_of_die

    def use(self, game_map, user = None):
        results = []

        results = self.spell(game_map=game_map,
                                caster=user,
                                target=user,
                                number_of_die=self.number_of_die,
                                type_of_die=self.type_of_die)
        results.append({ResultTypes.DISCARD_ITEM: self.owner})
        results.append({ResultTypes.END_TURN: True})

        return results

class ScrollUsable(Usable):
    def __init__(self, scroll_name="", scroll_spell=None, number_of_die=0, type_of_die=0, radius=3, targets_inventory=False):
        super().__init__(name=scroll_name)
        self.number_of_die = number_of_die
        self.radius = radius
        self.scroll_spell = scroll_spell
        self.type_of_die = type_of_die
        self.targets_inventory = targets_inventory

    def use(self, game_map, user = None, target = None, target_x=None, target_y=None):
        results = []

        if not target and self.targets_inventory:
            results.append({ResultTypes.TARGET_ITEM_IN_INVENTORY: self.owner})
        elif not target_x and self.needs_target:
            if self.targeting_message:
                results.append({ResultTypes.MESSAGE: self.targeting_message})
            results.append({ResultTypes.TARGETING: self.owner})
        else:
            results = self.scroll_spell(game_map=game_map,
                                        caster=user,
                                        target=target,
                                        number_of_die=self.number_of_die,
                                        type_of_die=self.type_of_die,
                                        radius=self.radius,
                                        target_x=target_x,
                                        target_y=target_y)
            results.append({ResultTypes.DISCARD_ITEM: self.owner})
            results.append({ResultTypes.END_TURN: True})
        return results
