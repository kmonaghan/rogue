import libtcodpy as libtcod
from random import choice, sample, randint

import bestiary
import equipment
import game_state
import quest
import random_utils

from components.ai import WanderingNPC
from components.stairs import Stairs

from entities.entity import Entity
from entities.character import Character
from entities.rat import Rat
from entities.snake import Snake, SnakeEgg

from map_objects.point import Point
from map_objects.rect import Rect
from map_objects.room import Room
from map_objects.tile import Tile
from map_objects.altbsptree import AltBSPTree
from map_objects.basic import Basic
from map_objects.bsptree import BSPTree
from map_objects.cellularautomata import CellularAutomata
from map_objects.mazewithrooms import MazeWithRooms
from map_objects.singleroom import SingleRoom

import map_objects.prefab

from render_order import RenderOrder

from game_messages import Message

from species import Species

class GameMap:
    def __init__(self, dungeon_level=0):
        self.width = 40
        self.height = 40
        self.map = None
        self.rooms = None
        self.npcs = []
        self.entities = []
        self.down_stairs = None
        self.dungeon_level = dungeon_level
        self.entity_map = None

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, offset=0):
        self.entities = [player]

        self.width = map_width
        self.height = map_height

        self.entity_map = [[[]
			for y in range(self.height)]
				for x in range(self.width)]

        #print "Generating Map sized: " + str(map_width) + " x " + str(map_height)
        #print "Dungeon level = " + str(self.dungeon_level)
        if (game_state.debug):
            generator = SingleRoom()
        elif (self.dungeon_level == 1):
            generator = CellularAutomata()
        elif (self.dungeon_level <= 2):
            generator = AltBSPTree()
        elif (self.dungeon_level <= 5):
            generator = MazeWithRooms()

        #generator = MazeWithRooms()
        #generator = BSPTree()
        #generator = CellularAutomata()
        #generator = Basic()

        if (self.dungeon_level == 6):
            prefabbed = map_objects.prefab.Prefab(map_objects.prefab.boss_room())
            generator.add_prefab(prefabbed)

        self.map = generator.generateLevel(map_width, map_height, max_rooms, room_min_size, room_max_size, offset)

        #print "Map size: " + str(len(self.map)) + " x " + str(len(self.map[0]))
        self.rooms = generator.rooms

        #print "Number of rooms: " + str(len(self.rooms))

        if (game_state.debug):
            self.test_popluate_map(player)
        elif (self.dungeon_level > 1):
            self.popluate_map(player)
        else:
            self.populate_cavern(player)

    #    if (game_state.debug):
    #        for room in self.rooms:
    #            self.add_npc_to_map(room.room_detail)

    def test_popluate_map(self, player):
        room = choice(self.rooms)
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.entities.append(self.down_stairs)

        for i in range(5):
            point = self.random_open_cell()
            npc = Snake(point)
            self.add_npc_to_map(npc)

        for i in range(10):
            point = self.random_open_cell()
            npc = Rat(point)
            self.add_npc_to_map(npc)

        for i in range(2):
            point = self.random_open_cell()
            npc = SnakeEgg(point)
            self.add_npc_to_map(npc)

    def populate_cavern(self, player):
        #Random room for player start
        room = choice(self.rooms)
        self.rooms.remove(room)
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        npc = bestiary.bountyhunter(room.random_tile(self))

        q = quest.kill_vermin()

        q2 = quest.Quest('Interloper', 'Someone has been sneaking around here. Find them and take care of it.', 100)
        q2.npc = bestiary.goblin(Point(0,0))
        q2.kill = 1
        q2.kill_type = Species.GOBLIN

        q.next_quest = q2

        npc.questgiver.add_quest(q)
        self.add_npc_to_map(npc)

        max_npcs = 40
        #choose random number of npcs
        num_npcs = libtcod.random_get_int(0, int(max_npcs/4), max_npcs)

        for i in range(int(num_npcs/2)):
            point = self.random_open_cell()
            npc = Snake(point)
            self.add_npc_to_map(npc)

        for i in range(int(num_npcs/2)):
            point = self.random_open_cell()
            npc = Rat(point)
            self.add_npc_to_map(npc)

        for i in range(10):
            point = self.random_open_cell()
            npc = SnakeEgg(point)
            self.add_npc_to_map(npc)

        stairs_component = Stairs(self.dungeon_level + 1)
        room = self.rooms[-1]
        self.rooms.remove(room)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.entities.append(self.down_stairs)

    def popluate_map(self, player):
        if (self.dungeon_level == 6):
            warlord = bestiary.warlord(Point(prefabbed.room.x1+5, prefabbed.room.y1 + 2))
            self.add_npc_to_map(warlord)
            self.rooms.remove(prefabbed.room)
        else:
            stairs_component = Stairs(self.dungeon_level + 1)
            room = self.rooms[-1]
            self.rooms.remove(room)
            self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
            self.entities.append(self.down_stairs)

        #Random room for player start
        room = choice(self.rooms)
        self.rooms.remove(room)
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        point = room.random_tile(self)
        npc = bestiary.bountyhunter(point)

        q = None

        if (self.dungeon_level == 2):
            q = quest.kill_gobbos()
        elif (self.dungeon_level == 3):
            q = quest.kill_orcs()
        elif (self.dungeon_level == 4):
            q = quest.kill_trolls()
        elif (self.dungeon_level == 6):
            q = quest.kill_warlord()

        if (q != None):
            if (self.dungeon_level == 2):
                q2 = quest.Quest('Kill the leader', 'Cut the head off and no more problem', 100)
                q2.npc = bestiary.goblin(Point(0,0))
                q.next_quest = q2
            elif (self.dungeon_level == 3):
                q2 = quest.Quest('Kill the leader', 'Cut the head off and no more problem', 100)
                q2.npc = bestiary.warlord(Point(0,0))
                q.next_quest = q2

            npc.questgiver.add_quest(q)
            self.add_npc_to_map(npc)

        #Add npcs and items
        for room in self.rooms:
            self.place_npc(room)
            self.place_object(room)

        if (len(self.rooms) > 4):
            num_to_select = 4                           # set the number to select here.
            list_of_random_items = sample(self.rooms, num_to_select)

            room = list_of_random_items[0]
            point = room.random_tile(self)
            npc = bestiary.goblin(point)
            npc.ai = WanderingNPC(list_of_random_items, npc.ai)
            npc.ai.owner = npc
            bestiary.upgrade_npc(npc)
            self.add_npc_to_map(npc)

#        point = self.rooms[2].random_tile(self)
#        necro = bestiary.necromancer(point)
#        self.add_npc_to_map(necro)

    def place_npc(self, room):
        #this is where we decide the chance of each npc or item appearing.

        #maximum number of npcs per room
        max_npcs = random_utils.from_dungeon_level([[2, 2], [3, 4], [5, 5]], self.dungeon_level)

        #chance of each npc
        npc_chances = {}
        npc_chances['goblin'] = random_utils.from_dungeon_level([[95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances['orc'] = random_utils.from_dungeon_level([[4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances['troll'] = random_utils.from_dungeon_level([[1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

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
                self.add_npc_to_map(npc)

        libtcod.namegen_destroy()

    def place_object(self, room):
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

                self.entities.append(item)
                #item.always_visible = True  #items are visible even out-of-FOV, if in an explored area

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1

        self.map = None
        self.rooms = None
        self.npcs = []
        self.entities = []
        self.down_stairs = None

        offset = 0
        if (self.dungeon_level <= 2):
            offset = 10

        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, offset)

        if (self.dungeon_level > 1):
            player.fighter.heal(player.fighter.max_hp // 2)

            message_log.add_message(Message('You take a moment to rest and recover your strength.', libtcod.light_violet))

        return self.entities

    def is_blocked(self, point):
        #first test the map tile
        if self.map[point.x][point.y].blocked:
            return True

        #now check for any blocking objects
        #for entity in self.entity_map[point.x][point.y]:
        #    if entity.blocks:
        #        return True

        return False

    def add_npc_to_map(self, npc):
        self.npcs.append(npc)
        self.entities.append(npc)

    def remove_npc_from_map(self, npc):
        self.npcs.remove(npc)
        self.entities.remove(npc)

    def get_blocking_entities_at_location(self, destination_x, destination_y):
        for entity in self.entities:
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity

        return None

    def check_for_stairs(self, x, y):
        if (self.down_stairs):
            if (self.down_stairs.x == x) and (self.down_stairs.y == y):
                return True
        return False

    def random_open_cell(self):
        tileX = randint(1,self.width - 2) #(2,mapWidth-3)
        tileY = randint(1,self.height - 2) #(2,mapHeight-3)
        point = Point(tileX, tileY)
        if not self.is_blocked(point):
            return point
        else:
            return self.random_open_cell()

    def add_to_map_state(self, entity):
        self.entity_map[entity.x][entity.y].append(entity)
        ##print "added " + entity.describe()

    def remove_from_map_state(self, entity):
        try:
            self.entity_map[entity.x][entity.y].remove(entity)
        except ValueError:
            pass
        ##print "removed " + entity.describe()

    def find_closest(self, point, species, max_distance=2):
        npc = None

        start_x = point.x - max_distance
        start_y = point.y - max_distance

        if (start_x < 0):
            start_x = 0

        if (start_y < 0):
            start_y = 0

        dist = max_distance + 1

        #print("Start looking from: (" + str(start_x) + ", " + str(start_y) +")")
        for x in range(start_x, start_x + (max_distance * 2) + 1):
            for y in range(start_y, start_y + (max_distance * 2) + 1):
                #print ("checking " + str(x) + ", " + str(y))
                self.map[x][y].color = libtcod.red
                if (len(self.entity_map[x][y])):
                    for entity in self.entity_map[x][y]:
                        if (point.x == x) and (point.y == y):
                            continue
                        #print ("checking: " + entity.describe())
                        if isinstance(entity, Character) and (entity.species == species) and not entity.isDead():
                            entity_distance = abs(x - point.x)
                            if (entity_distance < dist):
                                #print("FOUND!")
                                npc = entity
                #else:
                #    #print "no entites at " + str(x) + ", " + str(y)

        return npc

    def update_entity_map(self):
        self.entity_map = [[[]
                            for y in range(self.height)]
        				                for x in range(self.width)]
        for entity in self.entities:
            self.entity_map[entity.x][entity.y].append(entity)
