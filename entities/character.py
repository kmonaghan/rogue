__metaclass__ = type

import libtcodpy as libtcod

from entities.entity import Entity

import equipment

from components.equipment import Equipment
from components.inventory import Inventory
from components.level import Level

from render_order import RenderOrder
from species import Species
from game_states import debug

class Character(Entity):
    def __init__(self, point, char, name, color, always_visible=False, blocks=True, fighter=None, ai=None, item=None, gear=None, species=Species.NONDESCRIPT, death=None, health=None):
        super(Character, self).__init__(point, char, name, color, blocks, always_visible, fighter, ai, item, gear, death=death, health=health)

        self.inventory = Inventory(26)
        self.inventory.owner = self

        self.level = Level()
        self.level.owner = self

        self.equipment = Equipment()
        self.equipment.owner = self

        self.render_order = RenderOrder.ACTOR

        self.species = species

    def describe(self):
        desc = self.name.title()

        if (self.species == Species.GOBLIN):
            desc += " (Goblin)"
        elif (self.species == Species.ORC):
            desc += " (Orc)"
        elif (self.species == Species.TROLL):
            desc += " (Troll)"

        if (self.level):
            desc += " (Level " + str(self.level.current_level) + ")"

        if debug:
            desc += " (" + str(self.x) + ", " + str(self.y) +")"

        return desc

    def isDead(self):
        if (self.fighter):
            if (self.health.hp > 0):
                return False

        return True

    def onKill(self, npc, game_map):
        #print("Override onKill")
        pass

    def hasBeenAttacked(self, npc):
        #print("Override hasBeenAttacked")
        pass

    def upgradeNPC(npc):
        self.color = libtcod.silver
        self.fighter.multiplier = 1.5
        self.fighter.xp = npc.fighter.xp * 1.5
        item = equipment.random_magic_weapon()

        self.inventory.add_item(item)
        self.equipment.toggle_equip(item)
