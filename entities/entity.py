__metaclass__ = type

import libtcodpy as libtcod

import equipment
import math

from components.item import Item
from map_objects.point import Point

from game_messages import Message

from render_order import RenderOrder

import game_state

class Entity:
    #this is a generic object: the game_state.player, a npc, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, point, char, name, color, blocks=False, always_visible=False,
                 fighter=None, ai=None, item=None, stairs=None, equippable=None, render_order=RenderOrder.CORPSE):

        self.x = None
        self.y = None
        if point is not None:
            self.x = point.x
            self.y = point.y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible

        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self

        self.stairs = stairs
        if self.stairs:
            self.stairs.owner = self

        self.equippable = equippable
        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

        self.lootable = True

        self.questgiver = None

        self.description = None

        self.render_order = render_order

    @property
    def point(self):
        return Point(self.x,self.y)

    def examine(self):
        results = []

        detail = self.name.capitalize()
        if self.description:
            detail += ' ' + self.description()

        if self.equippable:
            detail += ' ' + self.equippable.equipment_description()

        results.append({'message': Message(detail, libtcod.gold)})

        return results

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        #if not is_blocked(Point(self.x + dx, self.y + dy)):
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        self.attempt_move(target_x, target_y, game_map)

    def attempt_move(self, target_x, target_y, game_map):
        if not (game_map.is_blocked(Point(target_x, target_y)) or
                game_map.get_blocking_entities_at_location(target_x, target_y)):
            self.move(target_x - self.x, target_y - self.y)
            return True

        return False

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

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
            self.move_towards(target.x, target.y, game_map)

            # Delete the path to free memory
        libtcod.path_delete(my_path)

    def display_color(self):
        if (self.fighter):
            return self.fighter.display_color()

        return self.color

    def describe(self):
        return self.name.capitalize()

    def setAI(self, ai):
        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self
