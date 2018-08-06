import libtcodpy as libtcod

from random import randint

import equipment

from components.ai import BasicNPC
from components.ai import Hunter
from components.ai import SpawnNPC

from components.fighter import Fighter

from entities.animal import Animal

from map_objects.point import Point

from species import Species

class Rat(Animal):
    def __init__(self, point = None):
        char = 'R'
        name = 'Rat'
        color = libtcod.darker_gray
        always_visible = False
        blocks = True
        fighter = Fighter(hp=4, defense=1, power=1, xp=2)
        ai = Hunter(attacked_ai = BasicNPC(), hunting = Species.EGG)
        item = None
        gear = None
        species = Species.RAT

        super(Rat, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)

        teeth = equipment.teeth()
        teeth.lootable = False

        self.inventory.add_item(teeth)
        self.equipment.toggle_equip(teeth)

        self.egg_generation = 0

class RatNest(Animal):
    def __init__(self, point = None):
        char = 'N'
        name = 'Rat Nest'
        color = libtcod.red
        always_visible = False
        blocks = True
        fighter = Fighter(hp=4, defense=1, power=0, xp=2)
        ai = SpawnNPC(Rat)
        item = None
        gear = None
        species = Species.RATNEST

        super(RatNest, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)

        teeth = equipment.teeth()
        teeth.lootable = False

        self.inventory.add_item(teeth)
        self.equipment.toggle_equip(teeth)

        self.egg_generation = 0

    def hasBeenAttacked(self, npc):
        print("Override hasBeenAttacked")
        
