__metaclass__ = type

import libtcodpy as libtcod
import gamemap
import equipment
import math
import screenrendering
import messageconsole

from map_objects.point import Point
from map_objects.map_utils import is_blocked

import game_state

fov_map = None

class Object:
    #this is a generic object: the pc.player, a npc, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, point, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, gear=None):
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

        self.equipment = gear
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.owner = self

            #there must be an Item component for the Equipment component to work properly
            self.item = equipment.Item()
            self.item.owner = self

        self.lootable = True

        self.questgiver = None

        self.description = None

    def examine(self):
        detail = self.name.capitalize()
        if self.description:
            detail += ' ' + self.description()

        if self.equipment:
            detail += ' ' + self.equipment.equipment_description()

        messageconsole.message(detail)

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not is_blocked(Point(self.x + dx, self.y + dy)):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        game_state.objects.remove(self)
        game_state.objects.insert(0, self)

    def draw(self):
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
                (self.always_visible and game_state.map[self.x][self.y].explored) or
                game_state.debug):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)

            x_offset = (gamemap.MAX_MAP_WIDTH - gamemap.MAP_WIDTH)/ 2
            y_offset = (gamemap.MAX_MAP_HEIGHT - gamemap.MAP_HEIGHT) / 2

            libtcod.console_put_char(con, self.x + x_offset, self.y + y_offset, self.char, libtcod.BKGND_NONE)

    def clear(self):
        x_offset = (gamemap.MAX_MAP_WIDTH - gamemap.MAP_WIDTH)/ 2
        y_offset = (gamemap.MAX_MAP_HEIGHT - gamemap.MAP_HEIGHT) / 2

        #erase the character that represents this object
        libtcod.console_put_char(con, self.x + x_offset, self.y + y_offset, ' ', libtcod.BKGND_NONE)

    def move_astar(self, target):
        #Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(gamemap.MAP_WIDTH, gamemap.MAP_HEIGHT)

        #Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(gamemap.MAP_HEIGHT):
            for x1 in range(gamemap.MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, not game_state.map[x1][y1].block_sight, not game_state.map[x1][y1].blocked)

        #Scan all the objects to see if there are objects that must be navigated around
        #Check also that the object isn't self or the target (so that the start and the end points are free)
        #The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for obj in game_state.objects:
            if obj.blocks and obj != self and obj != target:
                #Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)

        #Allocate a A* path
        #The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)

        #Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        #Check if the path exists, and in this case, also the path is shorter than 25 tiles
        #The path size matters if you want the npc to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        #It makes sense to keep path size relatively low to keep the npcs from running around the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            #Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                #Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            #Keep the old move function as a backup so that if there are no paths (for example another npc blocks a corridor)
            #it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y)

        #Delete the path to free memory
        libtcod.path_delete(my_path)

class Character(Object):
    def __init__(self, point, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, gear=None, level=None):
        super(Character, self).__init__(point, char, name, color, blocks, always_visible, fighter, ai, item, gear)
        self.inventory = []
        self.level = level
        if self.level:
            self.level.owner = self

    def get_equipped_in_slot(self, slot):  #returns the equipment in a slot, or None if it's empty
        for obj in self.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def get_all_equipped(self):  #returns a list of equipped items
        equipped_list = []
        for item in self.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list

    def add_to_inventory(self, obj):
        obj.owner = self
        self.inventory.append(obj)

    def remove_from_inventory(self, obj):
        self.inventory.remove(obj)
        obj.owner = None

    def list_quests(self):
        titles = []
        if len(game_state.active_quests) == 0:
            titles = [['No active quests.', libtcod.white]]
        else:
            for quest in game_state.active_quests:
                titles.append([quest.title, libtcod.white])

        index = screenrendering.menu("Quests", titles, screenrendering.INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(game_state.active_quests) == 0: return None

        messageconsole.message(quest.title, libtcod.white)
        messageconsole.message(quest.description, libtcod.white)

    def completed_quest(self, quest):
        if (self.fighter is not None):
            self.fighter.xp = self.fighter.xp + quest.xp

def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if gamemap.dungeon_level >= level:
            return value
    return 0

def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]
