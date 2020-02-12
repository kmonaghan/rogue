from random import randint

from components.poisoned import Poisoned

from etc.colors import COLORS
from etc.enum import DamageType, ResultTypes

from game_messages import Message

from utils.random_utils import die_roll
from utils.utils import coordinates_within_circle

class Aura:
    def __init__(self, name = "", range=1):
        self.owner = None
        self.name = name
        self.uuid = None

    def __str__(self):
        return f"{self.__class__} {self.name}"

    def __repr__(self):
        return f"{self.__class__} {self.name}"

    def on_turn(self, game_map):
        pass

class DamageAura(Aura):
    def __init__(self, name = "Damage Aura", range=0, number_of_dice=1, type_of_dice=6, damage_type=DamageType.DEFAULT):
        super().__init__(name = name, range = range)
        self.damage_type = damage_type
        self.range = range
        self.number_of_dice = number_of_dice
        self.type_of_dice = type_of_dice
        self.damage_type = damage_type

    def tick(self, game_map):
        results = []
        coords = coordinates_within_circle((self.owner.x, self.owner.y), self.range)
        for coord in coords:
            entities = game_map.current_level.entities.get_entities_in_position(coord)
            if entities:
                for entity in entities:
                    if entity == self.owner:
                        continue

                    if entity.health:
                        damage = die_roll(self.number_of_dice, self.type_of_dice)
                        damage_results, total_damage = entity.health.take_damage(damage, self.owner, self.damage_type)
                        if total_damage > 0:
                            msg = Message(f"{entity.name} takes {str(damage)} from {self.owner.name}'s {self.name} damage.", COLORS.get('damage_text'))
                            results.extend(damage_results)
                            results.extend([{ResultTypes.MESSAGE: msg}])

        return results
