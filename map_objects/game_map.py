import libtcodpy as libtcod
from random import choice, sample, randint

import bestiary
import equipment
import game_state
import quest
import random_utils

from components.ai import PatrollingNPC
from components.stairs import Stairs

from entities.entity import Entity
from entities.character import Character
from entities.chest import Chest
from entities.rat import Rat, RatNest
from entities.snake import Snake, SnakeEgg

from map_objects.point import Point
from map_objects.rect import Rect
from map_objects.tile import *

#import map_objects.prefab

from map_objects.dungeonGenerator import *

from render_order import RenderOrder

from game_messages import Message

from species import Species

class GameMap:
    def __init__(self, dungeon_level=1):
        self.entities = []
        self.down_stairs = None
        self.up_stairs = None
        self.dungeon_level = dungeon_level
        self.entity_map = None
        self.levels = [{},{},{},{},{},{}]
        self.generator = None

    @property
    def width(self):
        return self.generator.width

    @property
    def height(self):
        return self.generator.height

    @property
    def rooms(self):
        return self.generator.rooms

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, offset=0):
        self.entities = [player]

        if (self.dungeon_level == 1):
            self.generator = self.level_one_generator(map_width, map_height)
        else:
            boss_chance = randint(0,3) + dungeon_level
            if (self.dungeon_level >= 6):
                self.generator = self.level_boss_generator(map_width, map_height)
            else:
                self.generator = self.level_generator(map_width, map_height)

        '''
        EMPTY = 0
        FLOOR = 1
        CORRIDOR = 2
        DOOR = 3
        DEADEND = 4
        WALL = 5
        OBSTACLE = 6
        CAVE = 7
        '''

        self.map = [[Wall() for y in range(self.generator.height)]
                        for x in range(self.generator.width)]

        for x, y, tile in self.generator:
            if self.generator.grid[x][y] == DOOR:
                self.map[x][y] = Door()
            elif self.generator.grid[x][y] == FLOOR:
                self.map[x][y] = Floor()
            elif self.generator.grid[x][y] == WALL:
                self.map[x][y] = Wall()
            elif self.generator.grid[x][y] == CORRIDOR:
                self.map[x][y] = Ground()
            elif self.generator.grid[x][y] == CAVE:
                self.map[x][y] = Cave()
            elif self.generator.grid[x][y] == DEADEND:
                self.map[x][y] = Ground()

        self.level_one(player)
        #player.x = 0
        #player.y = 0

    def test_popluate_map(self, player):
        room = self.generator.rooms[-1]
        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.add_entity_to_map(self.down_stairs)

        room = self.generator.rooms[0]
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

    def level_one(self, player):
        room = self.generator.rooms[-1]
        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.add_entity_to_map(self.down_stairs)

        room = self.generator.rooms[0]
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        npc = bestiary.bountyhunter(room.random_tile(self))

        q = quest.kill_rats_nests()
        q2 = quest.Quest('Interloper', 'Someone has been sneaking around here. Find them and take care of it.', 100, start_func=self.level_one_goblin)
        q2.kill = 1
        q2.kill_type = Species.GOBLIN

        q.next_quest = q2

        q3 = quest.Quest('Go down', 'Find the stairs down', 100, map_point = self.down_stairs)
        q2.next_quest = q3

        npc.questgiver.add_quest(q)
        self.add_entity_to_map(npc)

        #Snakes and Rats
        for i in range(10):
            point = choice(self.generator.caves)
            npc = Snake(point)
            self.add_entity_to_map(npc)

        self.generator.findAlcoves()

        alcoves = self.generator.alcoves

        if (len(alcoves)):
            for i in range(6):
                point = choice(alcoves)
                alcoves.remove(point)
                npc = RatNest(point)
                self.add_entity_to_map(npc)

        if (len(alcoves)):
            point = choice(alcoves)
            chest = Chest(point, self.dungeon_level)
            self.add_entity_to_map(chest)

        num_rooms = len(self.generator.rooms)
        for room in self.generator.rooms[1:num_rooms]:
            num_npcs = libtcod.random_get_int(0, 0, 2)

            for i in range(num_npcs):
                npc = bestiary.goblin(room.random_tile(self))

                add_levels = self.dungeon_level + libtcod.random_get_int(0, -1, 1)
                npc.level.random_level_up(add_levels)

                self.add_entity_to_map(npc)

        room = choice(self.generator.rooms[1:num_rooms])
        chest2 = Chest(room.random_tile(self), self.dungeon_level)
        self.add_entity_to_map(chest2)
        '''
        #Potions and scrolls
        potion = equipment.healing_potion(Point(1,1))
        self.add_entity_to_map(potion)
        scroll1 = equipment.lighting_scroll(Point(1,2))
        self.add_entity_to_map(scroll1)
        scroll2 = equipment.fireball_scroll(Point(1,3))
        self.add_entity_to_map(scroll2)
        scroll3 = equipment.confusion_scroll(Point(1,4))
        self.add_entity_to_map(scroll3)
        '''

    def popluate_map(self, player):
        if (self.dungeon_level == 6):
            warlord = bestiary.warlord(Point(prefabbed.room.x1+5, prefabbed.room.y1 + 2))
            self.add_entity_to_map(warlord)
            self.generator.rooms.remove(prefabbed.room)
        else:
            stairs_component = Stairs(self.dungeon_level + 1)
            room = self.generator.rooms[-1]
            self.generator.rooms.remove(room)
            self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
            self.add_entity_to_map(self.down_stairs)

        #Random room for player start
        room = choice(self.generator.rooms)
        self.generator.rooms.remove(room)
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        stairs_component = Stairs(self.dungeon_level - 1)
        self.up_stairs = Entity(player.point, '<', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.add_entity_to_map(self.up_stairs)

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
            self.add_entity_to_map(npc)

        #Add npcs and items
        for room in self.generator.rooms:
            self.place_npc(room)
            self.place_object(room)

        if (len(self.generator.rooms) > 4):
            num_to_select = 4                           # set the number to select here.
            list_of_random_items = sample(self.generator.rooms, num_to_select)

            room = list_of_random_items[0]
            point = room.random_tile(self)
            npc = bestiary.goblin(point)
            npc.ai = PatrollingNPC(list_of_random_items, npc.ai)
            npc.ai.owner = npc
            bestiary.upgrade_npc(npc)
            self.add_entity_to_map(npc)

#        point = self.generator.rooms[2].random_tile(self)
#        necro = bestiary.necromancer(point)
#        self.add_entity_to_map(necro)

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
                choice = random_utils.random_choice_from_dict(npc_chances)
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
                self.add_entity_to_map(npc)

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
                choice = random_utils.random_choice_from_dict(item_chances)
                if choice == 'potion':
                    item = equipment.random_potion(point, self.dungeon_level)
                elif choice == 'scroll':
                    item = equipment.random_scroll(point, self.dungeon_level)
                elif choice == 'weapon':
                    item = equipment.random_weapon(point, self.dungeon_level)
                elif choice == 'armour':
                    item = equipment.random_armour(point, self.dungeon_level)

                self.add_entity_to_map(item)
                #item.always_visible = True  #items are visible even out-of-FOV, if in an explored area

    def create_floor(self, player, message_log, constants):
        self.entities = [player]
        self.down_stairs = None
        self.up_stairs = None

        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player)

        return self.entities

    def next_floor(self, player, message_log, constants):
        if (self.dungeon_level != 0):
            print("unloading map")
            self.unload_map()

        if (player.x == self.down_stairs.x) and (player.y == self.down_stairs.y):
            print("going down stairs")
            self.dungeon_level += 1
        else:
            print("going up stairs")
            self.dungeon_level -= 1

        if (len(self.levels[self.dungeon_level - 1])):
            print("loading a map")
            self.load_map()
            player.x = self.down_stairs.x
            player.y = self.down_stairs.y
        else:
            print("creating a new map")

            self.create_floor(player, message_log, constants)

            if (self.dungeon_level > 1):
                player.fighter.heal(player.fighter.max_hp // 2)

                message_log.add_message(Message('You take a moment to rest and recover your strength.', libtcod.light_violet))

        return self.entities

    def is_blocked(self, point):
        #first test the map tile
        if (point.x > self.generator.width):
            return False

        if (point.y > self.generator.height):
            return False

        if self.map[point.x][point.y].blocked:
            return True

        return False

    def add_entity_to_map(self, npc):
        self.entities.append(npc)

    def remove_npc_from_map(self, npc):
        self.entities.remove(npc)

    def get_blocking_entities_at_location(self, destination_x, destination_y):
        if (len(self.entity_map[destination_x][destination_y])):
            for entity in self.entity_map[destination_x][destination_y]:
                if entity.blocks:
                    return entity

        return None

    def check_for_stairs(self, x, y):
        if (self.down_stairs):
            if (self.down_stairs.x == x) and (self.down_stairs.y == y):
                return True

        if (self.up_stairs):
            if (self.up_stairs.x == x) and (self.up_stairs.y == y):
                return True

        return False

    def random_open_cell(self, start_x = 1, start_y = 1, end_x = -1, end_y = -1):
        if (end_x == -1):
            end_x = self.generator.width - 2

        if (end_y == -1):
            end_y = self.generator.height - 2

        tileX = randint(start_x, end_x)
        tileY = randint(start_y, end_y)

        point = Point(tileX, tileY)
        if not self.is_blocked(point):
            return point
        else:
            return self.random_open_cell(start_x, start_y, end_x, end_y)

    def find_closest(self, point, species, max_distance=2):
        npc = None

        start_x = point.x - max_distance
        start_y = point.y - max_distance

        if (start_x < 0):
            start_x = 0

        if (start_y < 0):
            start_y = 0

        end_x = start_x + (max_distance * 2) + 1
        if (end_x > self.generator.width):
            end_x = self.generator.width

        end_y = start_y + (max_distance * 2) + 1
        if (end_y > self.generator.height):
            end_y = self.generator.height

        dist = max_distance + 1

        #print("Start looking from: (" + str(start_x) + ", " + str(start_y) +")")
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                #print ("checking " + str(x) + ", " + str(y))

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
                            for y in range(self.generator.height)]
        				                for x in range(self.generator.width)]
        for entity in self.entities:
            self.entity_map[entity.x][entity.y].append(entity)

    def load_map(self):
        lmap = self.levels[self.dungeon_level - 1]
        self.entities = lmap["entities"]
        self.down_stairs = lmap["down_stairs"]
        self.up_stairs = lmap["up_stairs"]
        self.dungeon_level = lmap["dungeon_level"]
        self.entity_map = lmap["entity_map"]
        self.generator = lmap["generator"]

    def unload_map(self):
        print("unloading: " + str(self.dungeon_level))
        umap = {}
        umap["entities"] = self.entities
        umap["down_stairs"] = self.down_stairs
        umap["up_stairs"] = self.up_stairs
        umap["dungeon_level"] = self.dungeon_level
        umap["entity_map"] = self.entity_map
        umap["generator"] = self.generator

        self.levels[self.dungeon_level - 1] = umap

    def level_one_goblin(self):
        print("calling level_one_goblin from quest")
        point = self.random_open_cell(start_x=int(self.generator.width - ((self.generator.width / 3) * 2)), end_x = int(self.generator.width - (self.generator.width / 3)))
        npc = bestiary.goblin(point)

        add_levels = libtcod.random_get_int(0, -1, 1)
        npc.level.random_level_up(self.dungeon_level + add_levels)

        self.add_entity_to_map(npc)

    def level_one_generator(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        cave_width = int((map_width * 2)/ 3)
        caves = dungeonGenerator(width=cave_width, height=map_height - 2)

        caves.generateCaves(44, 3)
        # clear away small islands
        unconnected = dm.findUnconnectedAreas()
        for area in unconnected:
            if len(area) < 35:
                for x, y in area:
                    caves.grid[x][y] = EMPTY

        for x, y, tile in caves:
            dm.grid[x][y + 1] = caves.grid[x][y]

        dm.findCaves()

        startY = randint(1, dm.height - 5)
        dm.placeRoom(0, startY, 5, 5, ignoreOverlap = True)

        dm.placeRandomRooms(5, 9, 2, 2, 500)
        x, y = dm.findEmptySpace(3)
        while x:
            dm.generateCorridors('f', x, y)
            x, y = dm.findEmptySpace(3)
        # join it all together
        dm.connectAllRooms(0)

        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)

        dm.findDeadends()
        while len(dm.deadends):
            dm.pruneDeadends(1)

        dm.closeDeadDoors()
        dm.placeWalls()

        return dm

    def level_boss_generator(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        # generate rooms and corridors
        dm.placeRandomRooms(5, 9, 1, 1, 500)
        x, y = dm.findEmptySpace(3)
        while x:
            dm.generateCorridors('l', x, y)
            x, y = dm.findEmptySpace(3)
        # join it all together
        dm.connectAllRooms(0)
        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)
        dm.pruneDeadends(70)

        return dm

    def level_generator(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        '''
        3 options:
        1) all caverns
        2) both rooms and caverns
        3) all rooms
        '''

        chance = randint(0,100)

        print("Chance = " + str(chance))

        if (chance <= 66):
            print("Caverns")
            p = 37
            if (chance <= 33):
                p = 45
            dm.generateCaves(p, 4)
            # clear away small islands
            unconnected = dm.findUnconnectedAreas()
            for area in unconnected:
                if len(area) < 35:
                    for x, y in area:
                        dm.grid[x][y] = EMPTY

        if (chance > 33):
            print("Rooms")
            offset = 0
            if (chance > 66):
                offset = 2
            # generate rooms and corridors
            dm.placeRandomRooms(5 + offset, 9 + offset, 1 + offset, 1 + offset, 500)
            x, y = dm.findEmptySpace(3)
            while x:
                dm.generateCorridors('l', x, y)
                x, y = dm.findEmptySpace(3)
            # join it all together
            dm.connectAllRooms(0)

        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)
        dm.pruneDeadends(70)

        return dm
