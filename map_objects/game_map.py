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
from map_objects.dungeonGenerator import *
from map_objects.prefab import *

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
        self.map = None
        self.down_stairs_room = None
        self.up_stairs_room = None

    @property
    def width(self):
        return self.generator.width

    @property
    def height(self):
        return self.generator.height

    @property
    def rooms(self):
        return self.generator.rooms

    def make_map(self, map_width, map_height, player):
        self.entities = [player]

        boss_chance = randint(0,3) + self.dungeon_level

        if (self.dungeon_level == 1):
            self.generator = self.level_one_generator(map_width, map_height)
        else:
            if (boss_chance >= 6):
                self.generator = self.level_boss_generator(map_width, map_height)
            else:
                self.generator = self.level_generator(map_width, map_height)

        self.map = [[EmptyTile() for y in range(self.generator.height)]
                        for x in range(self.generator.width)]

        for x, y, tile in self.generator:
            if self.generator.grid[x][y] == Tiles.EMPTY:
                self.map[x][y] = EmptyTile()
            elif self.generator.grid[x][y] == Tiles.OBSTACLE:
                self.map[x][y] = EmptyTile()
            elif self.generator.grid[x][y] == Tiles.IMPENETRABLE:
                self.map[x][y] = EmptyTile()
            elif self.generator.grid[x][y] == Tiles.CAVERN_WALL:
                self.map[x][y] = CavernWall()
            elif self.generator.grid[x][y] == Tiles.CORRIDOR_WALL:
                self.map[x][y] = CorridorWall()
            elif self.generator.grid[x][y] == Tiles.ROOM_WALL:
                self.map[x][y] = RoomWall()
            elif self.generator.grid[x][y] == Tiles.DOOR:
                self.map[x][y] = Door()
            elif self.generator.grid[x][y] == Tiles.DEADEND:
                self.map[x][y] = CorridorWall()
            elif self.generator.grid[x][y] == Tiles.CAVERN_FLOOR:
                self.map[x][y] = CavernFloor()
            elif self.generator.grid[x][y] == Tiles.CORRIDOR_FLOOR:
                self.map[x][y] = CorridorFloor()
            elif self.generator.grid[x][y] == Tiles.ROOM_FLOOR:
                self.map[x][y] = RoomFloor()
            elif self.generator.grid[x][y] == Tiles.SHALLOWWATER:
                self.map[x][y] = ShallowWater()
            elif self.generator.grid[x][y] == Tiles.DEEPWATER:
                self.map[x][y] = DeepWater()
            else:
                self.map[x][y] = EmptyTile()

        if (self.dungeon_level == 1):
            self.level_one(player)
        else:
            if (boss_chance >= 6):
                self.level_boss(player)
            else:
                self.level_generic(player)

    def test_popluate_map(self, player):
        room = self.generator.rooms[0]
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

        q3 = quest.Quest('Go down', 'Find the stairs down', 100, map_point = self.down_stairs.point)
        q2.next_quest = q3

        npc.questgiver.add_quest(q)
        self.add_entity_to_map(npc)

        #Snakes and Rats
        for i in range(10):
            point = choice(self.generator.caves)
            npc = Snake(point)
            self.add_entity_to_map(npc)

        alcoves = self.generator.alcoves

        total_alcoves = len(alcoves)

        if (total_alcoves):
            nests = 6
            if (total_alcoves < nests):
                nests = total_alcoves

            for i in range(nests):
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

    def level_generic(self, player):
        if (len(self.generator.rooms)):
            '''
            room = self.generator.rooms[-1]
            downStairsPoint = room.random_tile(self)
            '''
            room = self.generator.rooms[0]

            playerStartPoint = room.random_tile(self)
        else:
            if (len(self.generator.alcoves)):
                alcoves = self.generator.alcoves
                downStairsPoint = choice(alcoves)
                alcoves.remove(downStairsPoint)

                playerStartPoint = choice(alcoves)
                alcoves.remove(playerStartPoint)
            else:
                print("No alcoves?!?!?")
                downStairsPoint = choice(self.generator.caves)
                playerStartPoint = choice(self.generator.caves)

        '''
        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(downStairsPoint, '>', 'Down Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.add_entity_to_map(self.down_stairs)
        '''
        player.x = playerStartPoint.x
        player.y = playerStartPoint.y

        up_stairs_component = Stairs(self.dungeon_level - 1)
        self.up_stairs = Entity(playerStartPoint, '<', 'Up Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=up_stairs_component)
        self.add_entity_to_map(self.up_stairs)

        self.place_creatures()

        #Add npcs and items
        for room in self.generator.rooms:
            self.place_npc(room)
            self.place_object(room)

        '''
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
        '''

    def level_boss(self, player):
        room = self.generator.rooms[0]
        warlord = bestiary.warlord(Point(room.x+5, room.y + 2))
        self.add_entity_to_map(warlord)

        room = self.generator.rooms[-1]
        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.add_entity_to_map(self.down_stairs)

        room = self.generator.rooms[-1]
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        stairs_component = Stairs(self.dungeon_level - 1)
        self.up_stairs = Entity(player.point, '<', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.add_entity_to_map(self.up_stairs)

        point = room.random_tile(self)
        npc = bestiary.bountyhunter(point)

        q = quest.kill_warlord()
        npc.questgiver.add_quest(q)
        self.add_entity_to_map(npc)

        #Add npcs and items
        for room in self.generator.rooms:
            self.place_npc(room)
            self.place_object(room)

    def place_creatures(self):
        npc_chances = {}
        npc_chances['rat'] = random_utils.from_dungeon_level([[95, 1], [95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances['snake'] = random_utils.from_dungeon_level([[95, 1], [4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances['snakeegg'] = random_utils.from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances['ratnest'] = random_utils.from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

        max_npcs = len(self.generator.caves) // 100

        num_npcs = libtcod.random_get_int(0, 0, max_npcs)

        print ("Max NPCs: " + str(max_npcs) + ", number of NPCs: " + str(num_npcs))

        alcoves = self.generator.alcoves

        for i in range(num_npcs):
            #choose random spot for this npc
            creature_choice = random_utils.random_choice_from_dict(npc_chances)

            if (creature_choice == 'ratnest') and len(alcoves):
                point = choice(alcoves)
                alcoves.remove(point)
                npc = RatNest(point)
                self.add_entity_to_map(npc)
            else:
                point = choice(self.generator.caves)

                #only place it if the tile is not blocked
                if not self.is_blocked(point):
                    if creature_choice == 'snake':
                        npc = Snake(point)
                    elif creature_choice == 'snakeegg':
                        npc = SnakeEgg(point)
                    elif creature_choice == 'rat':
                        npc = Rat(point)

                self.add_entity_to_map(npc)

    def place_npc(self, room):
        #this is where we decide the chance of each npc or item appearing.

        #maximum number of npcs per room
        max_npcs = random_utils.from_dungeon_level([[2, 2], [3, 4], [5, 5]], self.dungeon_level)

        #chance of each npc
        npc_chances = {}
        npc_chances['goblin'] = random_utils.from_dungeon_level([[95, 1],[95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances['orc'] = random_utils.from_dungeon_level([[95, 1],[4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances['troll'] = random_utils.from_dungeon_level([[95, 1],[95, 2], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

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

        self.make_map(constants['map_width'], constants['map_height'], player)

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

    def is_blocked(self, point, check_entities = False):
        #first test the map tile
        if (point.x < 0) or (point.x >= self.generator.width):
            return False

        if (point.y < 0) or (point.y >= self.generator.height):
            return False

        try:
            if self.map[point.x][point.y].blocked:
                return True
        except IndexError:
            print("is_blocked IndexError: " + point.describe())

        if (check_entities):
            if (self.get_blocking_entities_at_location(point)):
                return True

        return False

    def add_entity_to_map(self, npc):
        self.entities.append(npc)

    def remove_npc_from_map(self, npc):
        self.entities.remove(npc)

    def get_blocking_entities_at_location(self, point):
        try:
            if (len(self.entity_map[point.x][point.y])):
                for entity in self.entity_map[point.x][point.y]:
                    if entity.blocks:
                        return entity
        except IndexError:
            print("get_blocking_entities_at_location IndexError: " + point.describe())

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
            try:
                self.entity_map[entity.x][entity.y].append(entity)
            except IndexError:
                print("update_entity_map IndexError: " + entity.describe() + ' ' + entity.point.describe())

    def load_map(self):
        lmap = self.levels[self.dungeon_level - 1]
        self.entities = lmap["entities"]
        self.down_stairs = lmap["down_stairs"]
        self.up_stairs = lmap["up_stairs"]
        self.dungeon_level = lmap["dungeon_level"]
        self.entity_map = lmap["entity_map"]
        self.generator = lmap["generator"]
        self.map = lmap["map"]

    def unload_map(self):
        print("unloading: " + str(self.dungeon_level))
        umap = {}
        umap["entities"] = self.entities
        umap["down_stairs"] = self.down_stairs
        umap["up_stairs"] = self.up_stairs
        umap["dungeon_level"] = self.dungeon_level
        umap["entity_map"] = self.entity_map
        umap["generator"] = self.generator
        umap["map"] = self.map

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
        unconnected = caves.findUnconnectedAreas()
        for area in unconnected:
            if len(area) < 35:
                for x, y in area:
                    caves.grid[x][y] = Tiles.EMPTY

        for x, y, tile in caves:
            dm.grid[x][y + 1] = caves.grid[x][y]

        dm.findCaves()
        dm.findAlcoves()

        startY = randint(1, dm.height - 5)
        dm.placeRoom(1, startY, 5, 5, ignoreOverlap = True)

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

        dm.placeWalls()
        dm.closeDeadDoors()

        return dm

    def level_caverns(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        dm.generateCaves(45, 4)
        # clear away small islands
        unconnected = dm.findUnconnectedAreas()
        for area in unconnected:
            if len(area) < 35:
                for x, y in area:
                    dm.grid[x][y] = Tiles.EMPTY

        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)

        dm.findCaves()

        return dm

    def level_cavern_rooms(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        dm.generateCaves(37, 4)
        # clear away small islands
        unconnected = dm.findUnconnectedAreas()
        for area in unconnected:
            if len(area) < 35:
                for x, y in area:
                    dm.grid[x][y] = Tiles.EMPTY

        dm.findCaves()

        # generate rooms and corridors
        dm.placeRandomRooms(5, 10, 1, 1, 1000)
        x, y = dm.findEmptySpace(3)
        while x:
            dm.generateCorridors('f', x, y)
            x, y = dm.findEmptySpace(3)

        # join it all together
        dm.connectAllRooms(0)

        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)

        #clear all dead ends
        dm.findDeadends()
        while dm.deadends:
            dm.pruneDeadends(1)

        return dm

    def level_rooms(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        # generate rooms and corridors
        dm.placeRandomRooms(8, 12, 1, 1, 1000)
        x, y = dm.findEmptySpace(3)
        while x:
            dm.generateCorridors('l', x, y)
            x, y = dm.findEmptySpace(3)

        # join it all together
        dm.connectAllRooms(0)

        #clear all dead ends
        dm.findDeadends()
        while dm.deadends:
            dm.pruneDeadends(1)

        return dm

    def level_generator(self, map_width, map_height):

        '''
        3 options:
        1) all caverns
        2) both rooms and caverns
        3) all rooms
        '''

        chance = randint(0,100)

        if (chance <= 33):
            dm = self.level_caverns(map_width, map_height)
        elif (chance <= 66):
            dm = self.level_cavern_rooms(map_width, map_height)
        else:
            dm = self.level_rooms(map_width, map_height)

        lair = self.random_lair(map_width, map_height)
        if (lair):
            dm.placeRoom(lair.room.x, lair.room.y, lair.room.width, lair.room.height, ignoreOverlap = True)
            lair.carve(dm.grid)
            print(lair.room.describe())

        dm.placeWalls()
        dm.findAlcoves()

        self.down_stairs_room = self.place_stair_room(dm)
        self.up_stairs_room = self.place_stair_room(dm)

        return dm

    def level_boss_generator(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        prefab = Prefab(boss_room())

        startX = randint(1, map_width - prefab.room.width - 1)
        startY = randint(1, map_height - prefab.room.height - 2)

        dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = True)
        prefab.room.x = startX
        prefab.room.y = startY
        prefab.carve(dm.grid)
        print(prefab.room.describe())

        # generate rooms and corridors
        dm.placeRandomRooms(10, 15, 2, 2, 500)

        if (prefab.door):
            dm.generateCorridors('f', prefab.door.x, prefab.door.y + 2)
            dm.grid[prefab.door.x][prefab.door.y + 1] = Tiles.DOOR

        # join it all together
        dm.connectAllRooms(0)
        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)
        dm.pruneDeadends(70)
        dm.placeWalls()
        dm.closeDeadDoors()

        return dm

    def random_lair(self, map_width, map_height):
        lair_chance = False

        if (lair_chance):
            prefab = Prefab(necromancer_lair())

            startX = randint(1, map_width - prefab.room.width - 1)
            startY = randint(1, map_height - prefab.room.height - 2)

            prefab.room.x = startX
            prefab.room.y = startY

        #    point = prefab.room.random_tile(self)
        #    necro = bestiary.necromancer(point)
        #    self.add_entity_to_map(necro)

            return prefab

        return None

    def place_stair_room(self, dm):
        startX = randint(3, dm.width - 6)
        startY = randint(3, dm.height - 6)

        dm.placeRoom(startX, startY, 3, 3, ignoreOverlap = True)

        for x in range(startX - 1, startX + 4):
            print(str(x) + ',' + str(startY - 1))
            dm.grid[x][startY - 1] = Tiles.ROOM_WALL

        for x in range(startX - 1, startX + 4):
            print(str(x) + ',' + str(startY + 3))
            dm.grid[x][startY + 3] = Tiles.ROOM_WALL

        for y in range(startY - 1, startY + 4):
            dm.grid[startX - 1][y] = Tiles.ROOM_WALL

        for y in range(startY - 1, startY + 4):
            dm.grid[startX + 3][y] = Tiles.ROOM_WALL

        return dm.rooms[-1]
