__metaclass__ = type

import tcod as libtcod

from entities.entity import Entity

import equipment

from components.equipment import Equipment
from components.inventory import Inventory
from components.level import Level

from etc.configuration import CONFIG
from etc.enum import RenderOrder, Species

class Character(Entity):
    def __init__(self, point, char, name, color, always_visible=False, blocks=True, ai=None, item=None, gear=None, species=Species.NONDESCRIPT, death=None, health=None, act_energy=2):
        super(Character, self).__init__(point, char, name, color, blocks, always_visible, ai, item, gear, death=death, health=health, act_energy=act_energy)

        self.inventory = Inventory(26)
        self.inventory.owner = self

        self.equipment = Equipment()
        self.equipment.owner = self

        self.render_order = RenderOrder.ACTOR

        self.species = species

        self.subspecies = None

    def species_describe(self):
        desc = ""

        if (self.species == Species.GOBLIN):
            desc += "Goblin"
        elif (self.species == Species.ORC):
            desc += "Orc"
        elif (self.species == Species.TROLL):
            desc += "Troll"

        if self.subspecies:
            desc = self.subspecies.name + " " + desc

        return " (" + desc + ")"

    def describe(self):
        desc = self.name.title()

        desc += self.species_describe()

        if hasattr(self, 'level'):
            desc += " (Level " + str(self.level.current_level) + ")"

        if CONFIG.get('debug'):
            if self.offence:
                desc += " O:" + str(self.offence.power)
            if self.defence:
                desc += " D:" + str(self.defence.defence)

        return desc

    def display_color(self):
        if self.health and not self.health.dead and (self.health.health_percentage < 100):
            return self.health.display_color()

        if self.health and not self.health.dead and self.subspecies:
            return self.subspecies.subcolor

        return self.color
