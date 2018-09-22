import libtcodpy as libtcod
from random import randint

import equipment

from components.health import Health
from components.fighter import Fighter
from components.ai import BasicNPC

from entities.character import Character

from species import Species

class Chest(Character):
    def __init__(self, point, dungeon_level = 1):
        char = "C"
        name = "Chest"
        color= libtcod.blue
        always_visible = False
        blocks = True
        fighter = Fighter(defense=1, power=0, xp=0)
        health_component = Health(10)
        ai = None
        item = None
        gear = None
        species = Species.INANIMATE

        super(Chest, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)

        mimic_chance = randint(1, 100)

        if (mimic_chance >= 99):
            self.species = Species.CREATURE
            self.setFighter(Fighter(defense=3, power=3, xp=100))
            self.setHealth(Health(30))
            teeth = equipment.teeth()
            teeth.lootable = False

            self.inventory.add_item(teeth)
            self.equipment.toggle_equip(teeth)
        else:
            #TODO: Generate random level appropriate loot in chest
            potion = equipment.random_potion(dungeon_level=dungeon_level)
            potion.lootable = True

            scroll = equipment.random_scroll(dungeon_level=dungeon_level)
            scroll.lootable = True

            weapon = equipment.random_magic_weapon(dungeon_level=dungeon_level)
            weapon.lootable = True

            armour = equipment.random_armour(dungeon_level=dungeon_level)
            armour.lootable = True

            self.inventory.add_item(potion)
            self.inventory.add_item(scroll)
            self.inventory.add_item(weapon)
            self.inventory.add_item(armour)

    def hasBeenAttacked(self, npc):
        if (self.species == Species.CREATURE):
            self.name = 'Mimic'
            self.char = 'M'
            self.setAI(BasicNPC())
