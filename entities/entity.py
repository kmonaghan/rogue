__metaclass__ = type

import tcod as libtcod

import equipment
import math

from components.energy import Energy
from components.item import Item
from components.death import BasicDeath
from components.movement import Movement

from game_messages import Message

from map_objects.point import Point

from render_order import RenderOrder

import uuid

class Entity:
    #this is a generic object: the game_state.player, a npc, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, point, char, name, color, blocks=False, always_visible=False,
                 ai=None, item=None, stairs=None, equippable=None,
                 render_order=RenderOrder.CORPSE, death=None, health=None,
                 act_energy=2):

        self.x = None
        self.y = None
        if point is not None:
            self.x = point.x
            self.y = point.y
        self.char = char
        self.base_name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible

        self.health = health
        if self.health:  #let the health component know who owns it
            self.health.owner = self

        self.add_component(ai, "ai")
        self.add_component(item, "item")
        self.add_component(stairs, "stairs")
        self.add_component(Energy(act_energy), "energy")
        self.add_component(Movement(), "movement")

        self.equippable = equippable
        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

        self.lootable = True

        self.questgiver = None

        self.render_order = render_order

        self.death = death
        if self.death == None:
            self.death = BasicDeath()

        self.death.owner = self

        self.uuid = str(uuid.uuid4())

    @property
    def point(self):
        return Point(self.x,self.y)

    @property
    def name(self):
        real_name = self.base_name
        if self.health and self.health.dead:
            if self.death.skeletal:
                real_name = "Skeletal remains of " + real_name
            elif self.death.rotting:
                real_name = "Rotting corpse of " + real_name

        return real_name

    def examine(self):
        results = []

        detail = self.name.title()

        if self.equippable:
            detail += ' ' + self.equippable.equipment_description()

        results.append({ResultTypes.MESSAGE: Message(detail, libtcod.gold)})

        return results

    def display_color(self):
        if (self.health):
            return self.health.display_color()

        return self.color

    def describe(self):
        return self.name.title()

    def add_component(self, component, component_name):
        """Add a component as an attribute of the current object, and set the
        owner of the component to the current object.
        """
        if component:
            component.owner = self
        setattr(self, component_name, component)

    def del_component(self, component_name):
        """Remove a component as an attribute of the current object.
        """
        delattr(self, component_name)
