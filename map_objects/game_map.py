import libtcodpy as libtcod
from random import choice, sample

import bestiary
import equipment
import game_state
import quest
import random_utils

from components.ai import WanderingNPC
from components.stairs import Stairs

from entities.entity import Entity

from map_objects.point import Point
from map_objects.rect import Rect
from map_objects.room import Room
from map_objects.tile import Tile
from map_objects.altbsptree import AltBSPTree
from map_objects.basic import Basic
from map_objects.bsptree import BSPTree
from map_objects.cellularautomata import CellularAutomata
from map_objects.mazewithrooms import MazeWithRooms

import map_objects.prefab

from render_order import RenderOrder

from game_messages import Message

class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.map = None
        self.rooms = None

        self.dungeon_level = dungeon_level

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
        print "Generating Map sized: " + str(map_width) + " x " + str(map_height)

        if (self.dungeon_level <= 2):
            generator = AltBSPTree()
        elif (self.dungeon_level <= 5):
            generator = MazeWithRooms()

        #generator = MazeWithRooms()
        #generator = BSPTree()
        #generator = CellularAutomata()
        #generator = Basic()

        if (self.dungeon_level == 5):
            prefabbed = map_objects.prefab.Prefab(map_objects.prefab.boss_room())
            generator.add_prefab(prefabbed)

        self.map = generator.generateLevel(map_width, map_height, max_rooms, room_min_size, room_max_size)

        print "Map size: " + str(len(self.map)) + " x " + str(len(self.map[0]))
        self.rooms = generator.rooms

        print "Number of rooms: " + str(len(self.rooms))

        if (self.dungeon_level == 5):
            warlord = bestiary.warlord(Point(prefabbed.room.x1+5, prefabbed.room.y1 + 2))
            entities.append(warlord)
            self.rooms.remove(prefabbed.room)
        else:
            stairs_component = Stairs(self.dungeon_level + 1)
            room = self.rooms[-1]
            down_stairs = Entity(room.center(), '>', 'Stairs', libtcod.white, render_order=RenderOrder.STAIRS, stairs=stairs_component)
            entities.append(down_stairs)

        self.popluate_map(player, entities)

    def popluate_map(self, player, entities):
        #Random room for player start
        room = choice(self.rooms)
        self.rooms.remove(room)
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        point = room.random_tile(self)
        npc = bestiary.bountyhunter(point)

        q = None

        if (self.dungeon_level == 1):
            q = quest.kill_gobbos()
        elif (self.dungeon_level == 2):
            q = quest.kill_gobbos()
        elif (self.dungeon_level == 3):
            q = quest.kill_orcs()
        elif (self.dungeon_level == 4):
            q = quest.kill_trolls()
        elif (self.dungeon_level == 5):
            q = quest.kill_warlord()

        if (q != None):
            if (self.dungeon_level == 1):
                q2 = quest.Quest('Kill the leader', 'Cut the head off and no more problem', 100)
                q2.npc = bestiary.warlord(Point(0,0))
                q.next_quest = q2
            npc.questgiver.add_quest(q)
            entities.append(npc)

        #Add npcs and items
        for room in self.rooms:
            self.place_npc(room, entities)
            self.place_object(room, entities)

        if (len(self.rooms) > 4):
            num_to_select = 4                           # set the number to select here.
            list_of_random_items = sample(self.rooms, num_to_select)

            room = list_of_random_items[0]
            point = room.random_tile(self)
            npc = bestiary.goblin(point)
            npc.ai = WanderingNPC(list_of_random_items, npc.ai)
            npc.ai.owner = npc
            bestiary.upgrade_npc(npc)
            entities.append(npc)

    def place_npc(self, room, entities):
        #this is where we decide the chance of each npc or item appearing.

        #maximum number of npcs per room
        max_npcs = random_utils.from_dungeon_level([[2, 1], [3, 3], [5, 4]], self.dungeon_level)

        #chance of each npc
        npc_chances = {}
        npc_chances['goblin'] = random_utils.from_dungeon_level([[95, 1], [30, 2], [15, 3], [10, 4], [5, 5]], self.dungeon_level)
        npc_chances['orc'] = random_utils.from_dungeon_level([[4,1], [65, 2], [65, 3], [50, 4], [45, 5]], self.dungeon_level)
        npc_chances['troll'] = random_utils.from_dungeon_level([[1,1], [5, 2], [20, 3], [40, 4], [60, 5]], self.dungeon_level)

        #choose random number of npcs
        num_npcs = libtcod.random_get_int(0, 0, max_npcs)

        libtcod.namegen_parse('data/names.txt')

        for i in range(num_npcs):
            #choose random spot for this npc
            point = room.random_tile(self)

            #only place it if the tile is not blocked
            if not self.is_blocked(point):
                choice = random_utils.random_choice(npc_chances)
                if choice == 'orc':
                    npc = bestiary.orc(point)
                elif choice == 'troll':
                    npc = bestiary.troll(point)
                elif choice == 'goblin':
                    npc = bestiary.goblin(point)

                if (self.dungeon_level > 1):
                    add_levels = libtcod.random_get_int(0, -1, 1)

                    if (choice == 'goblin'):
                        npc.level.random_level_up(self.dungeon_level + add_levels - 1)

                    if ((self.dungeon_level > 2) and choice == 'orc'):
                        npc.level.random_level_up(self.dungeon_level + add_levels - 2)

                    if ((self.dungeon_level > 3) and choice == 'troll'):
                        npc.level.random_level_up(self.dungeon_level + add_levels - 3)

                npc.name = libtcod.namegen_generate(npc.name)
                entities.append(npc)

        libtcod.namegen_destroy()

    def place_object(self, room, entities):
        #maximum number of items per room
        max_items = random_utils.from_dungeon_level([[2, 1], [3, 4]], self.dungeon_level)

        #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        item_chances = {}
        item_chances['potion'] = 25  #healing potion always shows up, even if all other items have 0 chance
        item_chances['scroll'] = random_utils.from_dungeon_level([[25, 2]], self.dungeon_level)
        item_chances['weapon'] = 25
        item_chances['armour'] = 25

        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, max_items)

        for i in range(num_items):
            #choose random spot for this item
            point = room.random_tile(self)

            #only place it if the tile is not blocked
            if not self.is_blocked(point):
                choice = random_utils.random_choice(item_chances)
                if choice == 'potion':
                    item = equipment.random_potion(point)
                elif choice == 'scroll':
                    item = equipment.random_scroll(point)
                elif choice == 'weapon':
                    item = equipment.random_weapon(point)
                elif choice == 'armour':
                    item = equipment.random_armour(point)

                entities.append(item)
                #item.always_visible = True  #items are visible even out-of-FOV, if in an explored area

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

        return entities

    def is_blocked(self, point):
        #first test the map tile
    #    if (game_state.debug):
    #        print "Map size: " + str(len(game_state.map)) + " x " + str(len(game_state.map[0]))
    #        print "Testing: " + point.describe()

        if self.map[point.x][point.y].blocked:
            return True

        #now check for any blocking objects
        for object in game_state.objects:
            if object.blocks and object.x == point.x and object.y == point.y:
                return True

        return False
