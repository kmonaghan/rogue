__metaclass__ = type

import libtcodpy as libtcod

import game_state

from entities.entity import Entity

import equipment

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

        if (game_state.debug == True):
            desc += " (" + str(self.x) + ", " + str(self.y) +")"

        return desc

    def isDead(self):
        #print "am ded?"
        if (self.fighter):
            if (self.fighter.hp > 0):
                return False

        #print "not ded"
        return True

    def onKill(self, npc, game_map):
        print("Override onKill")

    def hasBeenAttacked(self, npc):
        print("Override hasBeenAttacked")

    def upgradeNPC(npc):
        self.color = libtcod.silver
        self.fighter.multiplier = 1.5
        self.fighter.xp = npc.fighter.xp * 1.5
        item = equipment.random_magic_weapon()

        self.inventory.add_item(item)
        self.equipment.toggle_equip(item)
