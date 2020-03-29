__metaclass__ = type

import equipment
import math

from components.energy import Energy
from components.item import Item
from components.interaction import Interaction
from components.death import BasicDeath
from components.movement import Movement

from game_messages import Message

from map_objects.point import Point

from etc.colors import COLORS, random_color_shimmer
from etc.enum import ResultTypes, RenderOrder, Interactions

import uuid

class Entity:
    #this is a generic object: the game_state.player, a npc, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, point, char, name, color, blocks=False, always_visible=False,
                 ai=None, item=None, equippable=None, render_order=RenderOrder.CORPSE,
                 death=None, health=None, usable=None, act_energy=3,
                 interaction=Interactions.FOE, animate=True, invisible=False):

        self.x = None
        self.y = None
        if point is not None:
            self.set_point(point)
        self.char = char
        self.base_name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.transparent = True
        self.animate = animate
        self.invisible = invisible

        self.add_component(health, "health")
        self.add_component(ai, "ai")
        self.add_component(item, "item")
        self.add_component(Energy(act_energy), "energy")
        self.add_component(Movement(), "movement")
        self.add_component(usable, "usable")

        self.equippable = equippable
        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

        self.lootable = True

        self.render_order = render_order

        if not death:
            death = BasicDeath()

        self.add_component(death, "death")

        self.add_component(Interaction(interaction), "interaction")

        self.uuid = str(uuid.uuid4())

        self.turn = {}

    def __str__(self):
        return f"{self.name.title()}"

    def __repr__(self):
        return f"{self.name.title()}"

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return None

    @property
    def point(self):
        return Point(self.x,self.y)

    def set_point(self, point):
        self.x = point.x
        self.y = point.y

    @property
    def name(self):
        if self.identifiable and not self.identifiable.identified:
            return self.identifiable.name

        if self.naming:
            return self.naming.fullname

        return self.base_name

    def examine(self):
        results = []

        detail = self.name.title()

        if self.equippable:
            detail += ' ' + self.equippable.equipment_description()

        results.append({ResultTypes.MESSAGE: Message(detail, COLORS.get('success_text'))})

        return results

    @property
    def display_char(self):
        if self.shimmer:
            return self.shimmer.display_char

        return self.char

    @property
    def display_color(self):
        if self.shimmer:
            return random_color_shimmer(self.color)

        if self.health:
            return self.health.display_color()

        return self.color

    def add_component(self, component, component_name):
        """Add a component as an attribute of the current object, and set the
        owner of the component to the current object.
        """
        if not component:
            return

        if component:
            component.owner = self

        #print(f"Adding component: {type(component).__name__}")

        setattr(self, component_name, component)

    def del_component(self, component_name):
        """Remove a component as an attribute of the current object.
        """

        try:
            delattr(self, component_name)
        except AttributeError:
            print(f"No component_name {component_name} to remove.")

    def register_turn(self, item):
        key = str(uuid.uuid4())
        self.turn[key] = item

        return key

    def deregister_turn(self, key):
        try:
            del self.turn[key]
        except KeyError:
            print(f"Key {key} not found")

    def deregister_turn_all(self):
        self.turn.clear()

    def on_turn(self, game_map):
        results = []

        if self.movement:
            self.movement.has_moved = False

        turn_copy = self.turn.copy()
        for key in turn_copy:
            try:
                results.extend(turn_copy[key].tick(game_map))
            except TypeError as e:
                print(f"Error proccessing turn: {e}")

        return results

    def clone(self):
        for att in dir(self):
            print (att, getattr(self, att))
