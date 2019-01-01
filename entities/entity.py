__metaclass__ = type

import libtcodpy as libtcod

import equipment
import math

from components.energy import Energy
from components.item import Item
from components.death import BasicDeath
from map_objects.point import Point

from game_messages import Message

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

        results.append({'message': Message(detail, libtcod.gold)})

        return results

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        #if not is_blocked(Point(self.x + dx, self.y + dy)):
        self.x += dx
        self.y += dy

    def move_towards(self, target_point, game_map):
        tx = target_point.x - self.x
        ty = target_point.y - self.y

        dx = tx
        dy = ty

        if (tx < 0):
            dx = -1
        elif (tx > 0):
            dx = 1

        if (ty < 0):
            dy = -1
        elif (ty > 0):
            dx = 1

        self.attempt_move(Point(self.x + dx, self.y + dy), game_map)

    def attempt_move(self, target_point, game_map):
        if not game_map.is_blocked(target_point, True):
            self.x = target_point.x
            self.y = target_point.y

            return True

        return False

    def move_astar(self, target, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.map[x1][y1].block_sight,
                                           not game_map.map[x1][y1].blocked)

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in game_map.entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 100: #25:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.point, game_map)

            # Delete the path to free memory
        libtcod.path_delete(my_path)

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
