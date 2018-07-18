__metaclass__ = type

import libtcodpy as libtcod

from entities.entity import Entity

from components.equipment import Equipment
from components.inventory import Inventory
from components.level import Level

from render_order import RenderOrder
from species import Species

class Character(Entity):
    def __init__(self, point, char, name, color, always_visible=False, blocks=True, fighter=None, ai=None, item=None, gear=None, species=Species.NONDESCRIPT):
        super(Character, self).__init__(point, char, name, color, blocks, always_visible, fighter, ai, item, gear)

        self.inventory = Inventory(26)
        self.inventory.owner = self

        self.level = Level()
        self.level.owner = self

        self.equipment = Equipment()
        self.equipment.owner = self

        self.render_order = RenderOrder.ACTOR

        self.species = species

    def describe(self):
        desc = self.name.capitalize()

        if (self.species == Species.GOBLIN):
            desc += "(Goblin)"
        elif (self.species == Species.ORC):
            desc += "(Orc)"
        elif (self.species == Species.TROLL):
            desc += "(Troll)"

        return desc
