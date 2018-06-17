__metaclass__ = type

import libtcodpy as libtcod

import game_state
import screenrendering

from entities.object import Object

from components.equipment import Equipment
from components.inventory import Inventory
from components.level import Level

from render_order import RenderOrder

class Character(Object):
    def __init__(self, point, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, gear=None):
        super(Character, self).__init__(point, char, name, color, blocks, always_visible, fighter, ai, item, gear)

        self.inventory = Inventory(26)
        self.inventory.owner = self

        self.level = Level()
        self.level.owner = self

        self.equipment = Equipment()
        self.equipment.owner = self

        self.render_order = RenderOrder.ACTOR
