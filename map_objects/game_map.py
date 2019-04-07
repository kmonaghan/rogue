import tcod as libtcod
from random import choice, sample, randint, getrandbits

import bestiary
import equipment
import quest
import random_utils

from components.ai import PatrollingNPC
from components.stairs import Stairs

from entities.entity import Entity
from entities.character import Character

from map_objects.point import Point
from map_objects.rect import Rect
from map_objects.tile import *
from map_objects.dungeonGenerator import *
from map_objects.prefab import *
from map_objects.level_map import LevelMap

from etc.enum import RenderOrder, RoutingOptions, Species

class GameMap:
    def __init__(self, dungeon_level=1):
        self.dungeon_level = dungeon_level
        self.levels = [{},{},{},{},{},{}]
        self.current_level = None

    def make_map(self, map_width, map_height, player):

        boss_chance = randint(0,3) + self.dungeon_level


        if (self.dungeon_level == 1):
            self.current_level = self.level_one_generator(map_width, map_height)
        else:
            if (boss_chance >= 6):
                self.current_level = self.level_boss_generator(map_width, map_height)
            else:
                self.current_level = self.level_generator(map_width, map_height)

        self.current_level.dungeon_level = self.dungeon_level
        '''

        self.current_level = self.arena(map_width, map_height)
        self.test_popluate_map(player)

        #self.current_level = self.level_generator(map_width, map_height)
        #self.current_level.dungeon_level = self.dungeon_level

        #self.level_generic(player)
        return
        '''

        if (self.dungeon_level == 1):
            self.level_one(player)
        else:
            if (boss_chance >= 6):
                self.level_boss(player)
            else:
                self.level_generic(player)

    def test_popluate_map(self, player):
        room = self.current_level.floor.rooms[0]
        stairs_component = Stairs(self.dungeon_level + 1)
        #self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        #self.current_level.add_down_stairs(self.down_stairs)

        point = room.center_tile()
        player.x = point.x
        player.y = point.y
        self.current_level.add_entity(player)

        # npc = bestiary.generate_npc(Species.TROLL, self.dungeon_level, player.level.current_level, room.random_tile(self))
        # bestiary.upgrade_npc(npc)
        #for i in range(5):
        #    snake = bestiary.generate_creature(Species.SNAKE, self.dungeon_level, player.level.current_level, room.random_tile(self))
        #    self.current_level.add_entity(snake)
        #
        #for i in range(5):
        #    rat = bestiary.generate_creature(Species.RAT, self.dungeon_level, player.level.current_level, room.random_tile(self))
        #    self.current_level.add_entity(rat)
        #
        #for i in range(5):
        #    rat = bestiary.generate_creature(Species.RATNEST, self.dungeon_level, player.level.current_level, room.random_tile(self))
        #    self.current_level.add_entity(rat)
        #
        #for i in range(5):
        #    egg = bestiary.generate_creature(Species.EGG, self.dungeon_level, player.level.current_level, room.random_tile(self))
        #    self.current_level.add_entity(egg)

        #pt = room.random_tile(self)
        '''
        for i in range(3):
            pt = self.current_level.find_random_open_position([], room = room)
            npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level, pt)
            bestiary.upgrade_npc(npc)
            self.current_level.add_entity(npc)
        '''
        #Add npcs and items
        for room in self.current_level.floor.rooms:
            self.place_npc(room, player)
            self.place_object(room)
        #for i in range(1):
        #    #chest = bestiary.create_chest(room.random_tile(self), self.dungeon_level)
        #    #self.current_level.add_entity(chest)
        #    bestiary.place_chest(room.random_tile(self), self)

        '''
        #Potions, scrolls and rings
        potion = equipment.healing_potion(Point(1,1))
        self.current_level.add_entity(potion)
        scroll1 = equipment.lighting_scroll(Point(1,2))
        self.current_level.add_entity(scroll1)
        scroll2 = equipment.fireball_scroll(Point(1,3))
        self.current_level.add_entity(scroll2)
        scroll3 = equipment.confusion_scroll(Point(1,4))
        self.current_level.add_entity(scroll3)
        scroll4 = equipment.map_scroll(player.point)
        self.current_level.add_entity(scroll4)
        ring1 = equipment.ring_of_power(player.point)
        self.current_level.add_entity(ring1)
        ring2 = equipment.ring_of_defence(player.point)
        self.current_level.add_entity(ring2)
        '''

    def level_one(self, player):
        room = self.current_level.floor.rooms[-1]
        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.current_level.add_entity(self.down_stairs)
        self.current_level.downward_stairs_position = (self.down_stairs.x, self.down_stairs.y)

        room = self.current_level.floor.rooms[0]
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y
        self.current_level.add_entity(player)

        npc = bestiary.bountyhunter(room.random_tile(self))

        q = quest.kill_rats_nests()
        q2 = quest.Quest('Interloper', 'Someone has been sneaking around here. Find them and take care of it.', 100, start_func=self.level_one_goblin)
        q2.kill = 1
        q2.kill_type = Species.GOBLIN

        q.next_quest = q2

        q3 = quest.Quest('Go down', 'Find the stairs down', 100, map_point = self.down_stairs.point)
        q2.next_quest = q3

        npc.questgiver.add_quest(q)
        self.current_level.add_entity(npc)

        #Snakes and Rats
        for i in range(10):
            point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                    RoutingOptions.AVOID_DOORS,
                                                                    RoutingOptions.AVOID_FLOORS,
                                                                    RoutingOptions.AVOID_STAIRS])
            snake = bestiary.generate_creature(Species.SNAKE, self.dungeon_level, player.level.current_level, point)
            self.current_level.add_entity(snake)

            point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                    RoutingOptions.AVOID_DOORS,
                                                                    RoutingOptions.AVOID_FLOORS,
                                                                    RoutingOptions.AVOID_STAIRS])
            rat = bestiary.generate_creature(Species.RAT, self.dungeon_level, player.level.current_level, point)
            self.current_level.add_entity(rat)

        for i in range(6):
            point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                    RoutingOptions.AVOID_DOORS,
                                                                    RoutingOptions.AVOID_FLOORS,
                                                                    RoutingOptions.AVOID_STAIRS])
            nest = bestiary.generate_creature(Species.RATNEST, self.dungeon_level, player.level.current_level, point)
            self.current_level.add_entity(nest)

        point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                RoutingOptions.AVOID_DOORS,
                                                                RoutingOptions.AVOID_FLOORS,
                                                                RoutingOptions.AVOID_STAIRS])
        bestiary.place_chest(point, self.current_level)

        num_rooms = len(self.current_level.floor.rooms)
        for room in self.current_level.floor.rooms[1:num_rooms]:
            num_npcs = libtcod.random_get_int(0, 0, 2)

            for i in range(num_npcs):
                npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level, room.random_tile(self))

                self.current_level.add_entity(npc)

        room = choice(self.current_level.floor.rooms[1:num_rooms])
        bestiary.place_chest(room.random_tile(self), self.current_level)

    def level_generic(self, player):
        self.current_level.add_entity(self.down_stairs)
        self.current_level.add_entity(self.up_stairs)

        self.current_level.downward_stairs_position = (self.down_stairs.x, self.down_stairs.y)
        self.current_level.upward_stairs_position = (self.up_stairs.x, self.up_stairs.y)

        player.x = self.up_stairs.x
        player.y = self.up_stairs.y
        self.current_level.add_entity(player)


        if len(self.current_level.floor.caves) > 0:
            self.place_creatures(player)

        '''
        for room in self.current_level.floor.rooms:
            self.place_npc(room, player)
            self.place_object(room)


        if (len(self.current_level.floor.rooms) > 4):
            num_to_select = 4                           # set the number to select here.
            list_of_random_items = sample(self.current_level.floor.rooms, num_to_select)

            room = list_of_random_items[0]
            point = room.random_tile(self)
            npc = bestiary.goblin(point)
            npc.ai = PatrollingNPC(list_of_random_items, npc.ai)
            npc.ai.owner = npc
            bestiary.upgrade_npc(npc)
            self.current_level.add_entity(npc)
        '''

    def level_boss(self, player):
        room = self.current_level.floor.rooms[0]
        warlord = bestiary.warlord(Point(room.x+5, room.y + 2))
        self.current_level.add_entity(warlord)

        room = self.current_level.floor.rooms[-1]
        stairs_component = Stairs(self.dungeon_level + 1)
        self.down_stairs = Entity(room.random_tile(self), '>', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.current_level.add_entity(self.down_stairs)

        room = self.current_level.floor.rooms[-1]
        point = room.random_tile(self)
        player.x = point.x
        player.y = point.y

        stairs_component = Stairs(self.dungeon_level - 1)
        self.up_stairs = Entity(player.point, '<', 'Stairs', libtcod.silver, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        self.current_level.add_entity(self.up_stairs)

        point = room.random_tile(self)
        npc = bestiary.bountyhunter(point)

        q = quest.kill_warlord()
        npc.questgiver.add_quest(q)
        self.current_level.add_entity(npc)

        #Add npcs and items
        for room in self.current_level.floor.rooms:
            self.place_npc(room, player)
            self.place_object(room)

    def place_creatures(self, player):
        npc_chances = {}
        npc_chances[Species.RAT] = random_utils.from_dungeon_level([[95, 1], [95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances[Species.SNAKE] = random_utils.from_dungeon_level([[95, 1], [4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances[Species.EGG] = random_utils.from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances[Species.RATNEST] = random_utils.from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances[Species.BAT] = random_utils.from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

        max_npcs = len(self.current_level.floor.caves) // 100

        num_npcs = randint(1,max_npcs)

        print ("Max NPCs: " + str(max_npcs) + ", number of NPCs: " + str(num_npcs))

        for i in range(num_npcs):
            #choose random spot for this npc
            creature_choice = random_utils.random_choice_from_dict(npc_chances)

            print(creature_choice)

            point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                    RoutingOptions.AVOID_DOORS,
                                                                    RoutingOptions.AVOID_FLOORS])

            npc = bestiary.generate_creature(creature_choice, self.dungeon_level, player.level.current_level, point)
            self.current_level.add_entity(npc)

    def place_npc(self, room, player):
        #this is where we decide the chance of each npc or item appearing.

        #maximum number of npcs per room
        max_npcs = 4# random_utils.from_dungeon_level([[1,2], [2, 2], [3, 4], [5, 5]], self.dungeon_level)

        #chance of each npc
        npc_chances = {}
        npc_chances[Species.GOBLIN] = random_utils.from_dungeon_level([[95, 1],[95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances[Species.ORC] = random_utils.from_dungeon_level([[95, 1],[4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances[Species.TROLL] = random_utils.from_dungeon_level([[95, 1],[95, 2], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

        #choose random number of npcs
        num_npcs = randint(1, max_npcs)

        for i in range(num_npcs):
            point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                    RoutingOptions.AVOID_DOORS],
                                                                    room = room)
            choice = random_utils.random_choice_from_dict(npc_chances)
            npc = bestiary.generate_npc(choice, self.dungeon_level, player.level.current_level, point)
            self.current_level.add_entity(npc)

    def place_object(self, room):
        return
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
            if not self.current_level.blocked[point.x, point.y]:
                choice = random_utils.random_choice_from_dict(item_chances)
                if choice == 'potion':
                    item = equipment.random_potion(point, self.dungeon_level)
                elif choice == 'scroll':
                    item = equipment.random_scroll(point, self.dungeon_level)
                elif choice == 'weapon':
                    item = equipment.random_weapon(point, self.dungeon_level)
                elif choice == 'armour':
                    item = equipment.random_armour(point, self.dungeon_level)

                self.current_level.add_entity(item)

    def create_floor(self, player, constants):
        self.down_stairs = None
        self.up_stairs = None

        self.make_map(constants['map_width'], constants['map_height'], player)

    def next_floor(self, player, constants):
        #TODO: Re-implement loading/unloading of maps
        '''
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
        '''
        #if (player.x == self.down_stairs.x) and (player.y == self.down_stairs.y):
        #    print("going down stairs")
        #    self.dungeon_level += 1
        #else:
        #    print("going up stairs")
        #    self.dungeon_level -= 1

        self.dungeon_level += 1

        self.create_floor(player, constants)

        if (self.dungeon_level > 1):
            player.health.heal(player.health.max_hp // 2)

    def check_for_stairs(self, x, y):
        if (self.down_stairs):
            if (self.down_stairs.x == x) and (self.down_stairs.y == y):
                return True

        if (self.up_stairs):
            if (self.up_stairs.x == x) and (self.up_stairs.y == y):
                return True

        return False

    def load_map(self):
        lmap = self.levels[self.dungeon_level - 1]
        self.down_stairs = lmap["down_stairs"]
        self.up_stairs = lmap["up_stairs"]
        self.dungeon_level = lmap["dungeon_level"]
        self.generator = lmap["generator"]
        self.map = lmap["map"]

    def unload_map(self):
        print("unloading: " + str(self.dungeon_level))
        umap = {}
        umap["down_stairs"] = self.down_stairs
        umap["up_stairs"] = self.up_stairs
        umap["dungeon_level"] = self.dungeon_level
        umap["generator"] = self.generator
        umap["map"] = self.map

        self.levels[self.dungeon_level - 1] = umap

    def level_one_goblin(self):
        point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                RoutingOptions.AVOID_DOORS,
                                                                RoutingOptions.AVOID_FLOORS,
                                                                RoutingOptions.AVOID_STAIRS])

        self.current_level.add_entity(bestiary.generate_npc(Species.GOBLIN, 1, 1, point))

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
                    caves.dungeon.grid[x][y] = Tiles.EMPTY

        for x, y, tile in caves:
            dm.dungeon.grid[x][y + 1] = caves.dungeon.grid[x][y]

        dm.findCaves()
        #dm.findAlcoves()

        startY = randint(1, dm.dungeon.height - 6)
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
        while len(dm.dungeon.deadends):
            dm.pruneDeadends(1)

        dm.placeWalls()
        dm.closeDeadDoors()

        return LevelMap(dm.dungeon)

    def level_caverns(self, dm):
        dm.generateCaves(45, 4)
        # clear away small islands
        unconnected = dm.findUnconnectedAreas()
        for area in unconnected:
            if len(area) < 10:
                for x, y in area:
                    dm.dungeon.grid[x][y] = Tiles.EMPTY

        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected, Tiles.CAVERN_FLOOR)

        dm.findCaves()
        dm.placeWalls()

        return dm

    def level_cavern_rooms(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        dm.generateCaves(37, 4)
        # clear away small islands
        unconnected = dm.findUnconnectedAreas()
        for area in unconnected:
            if len(area) < 35:
                for x, y in area:
                    dm.dungeon.grid[x][y] = Tiles.EMPTY

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
        while dm.dungeon.deadends:
            dm.pruneDeadends(1)

        return dm

    def level_rooms(self, dm):
        # generate rooms and corridors
        dm.placeRandomRooms(8, 12, 1, 1, 1000)
        x, y = dm.findEmptySpace(3)
        while x:
            dm.generateCorridors('f', x, y)
            x, y = dm.findEmptySpace(3)

        # join it all together
        dm.connectAllRooms(0)

        #clear all dead ends
        dm.findDeadends()
        while dm.dungeon.deadends:
            dm.pruneDeadends(1)

    def level_generator(self, map_width, map_height):

        '''
        3 options:
        1) all caverns
        2) both rooms and caverns
        3) all rooms
        '''

        dm = dungeonGenerator(width=map_width, height=map_height)

        self.place_stair_room(dm)
        self.down_stairs = Entity(dm.dungeon.rooms[-1].center_tile(), '>', 'Down Stairs',
                                    libtcod.silver, render_order=RenderOrder.STAIRS,
                                    stairs=Stairs(self.dungeon_level + 1))
        self.place_stair_room(dm)
        self.up_stairs = Entity(dm.dungeon.rooms[-1].center_tile(), '<', 'Up Stairs',
                                libtcod.silver, render_order=RenderOrder.STAIRS,
                                stairs=Stairs(self.dungeon_level - 1))

        self.level_rooms(dm)

        return LevelMap(dm.dungeon)

        chance = randint(0,100)
        '''
        if (chance <= 33):
            dm = self.level_caverns(dm)
        elif (chance <= 66):
            dm = self.level_cavern_rooms(map_width, map_height)
        else:
            dm = self.level_rooms(map_width, map_height)
        '''

        self.random_lair(dm)

        self.place_stair_room(dm)
        self.down_stairs = Entity(dm.dungeon.rooms[-1].center_tile(), '>', 'Down Stairs',
                                    libtcod.silver, render_order=RenderOrder.STAIRS,
                                    stairs=Stairs(self.dungeon_level + 1))
        self.place_stair_room(dm)
        self.up_stairs = Entity(dm.dungeon.rooms[-1].center_tile(), '<', 'Up Stairs',
                                libtcod.silver, render_order=RenderOrder.STAIRS,
                                stairs=Stairs(self.dungeon_level - 1))

        dm = self.level_caverns(dm)

        return LevelMap(dm.dungeon)

    def level_boss_generator(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        prefab = Prefab(boss_room())

        self.place_prefab(prefab, dm)

        # generate rooms and corridors
        dm.placeRandomRooms(10, 15, 2, 2, 500)

        if (prefab.door):
            dm.generateCorridors('f', prefab.door.x, prefab.door.y + 2)
            dm.dungeon.grid[prefab.door.x][prefab.door.y + 1] = Tiles.DOOR

        # join it all together
        dm.connectAllRooms(0)
        unconnected = dm.findUnconnectedAreas()
        dm.joinUnconnectedAreas(unconnected)
        dm.pruneDeadends(70)
        dm.placeWalls()
        dm.closeDeadDoors()

        return LevelMap(dm.dungeon)

    def random_lair(self, dm):
        lair_chance = True

        if (lair_chance):
            prefab = Prefab(necromancer_lair())

            self.place_prefab(prefab, dm)

            #point = prefab.room.random_tile(self)
            #necro = bestiary.necromancer(point)
            #self.current_level.add_entity(necro)

    def place_stair_room(self, dm):
        prefab = Prefab(stair_room())

        self.place_prefab(prefab, dm)

    def place_prefab(self, prefab, dm):
        startX, startY = dm.placeRoomRandomly(prefab.room.width, prefab.room.height)

        prefab.room.x = startX
        prefab.room.y = startY

        dm.placeRoom(prefab.room.x, prefab.room.y, prefab.room.width, prefab.room.height)
        prefab.carve(dm.dungeon.grid)

    def arena(self, map_width, map_height):
        dm = dungeonGenerator(width=map_width, height=map_height)

        prefab = self.circle_shaped_room(circle_size = 15)
        startX = (map_width // 2) - (prefab.room.width // 2)
        startY = (map_height // 2) - (prefab.room.height // 2)
        dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = False)
        prefab.room.x = startX
        prefab.room.y = startY
        prefab.carve(dm.dungeon.grid)

        for x in range(3):
            prefab = self.circle_shaped_room()
            startX, startY = dm.placeRoomRandomly(prefab.room.width, prefab.room.height)
            dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = False)
            prefab.room.x = startX
            prefab.room.y = startY
            prefab.carve(dm.dungeon.grid)

        for x in range(5):
            prefab = self.curved_side_shaped_room()
            startX, startY = dm.placeRoomRandomly(prefab.room.width, prefab.room.height)
            dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = True)
            prefab.room.x = startX
            prefab.room.y = startY
            prefab.carve(dm.dungeon.grid)

        dm.placeWalls()

        return LevelMap(dm.dungeon)

    def circle_shaped_room(self, donut=False, circle_size = 0):

        if circle_size == 0:
            circle_size = randrange(5, 15, 2)

        floor_size = 3

        start_inset = (circle_size - floor_size) // 2
        end_inset = circle_size - start_inset - 1

        room_layout = [[i for i in range(circle_size)] for i in range(circle_size)]

        offset = 0

        for y in range(circle_size):
            for x in range(circle_size):
                if (x < (start_inset - offset)):
                    room_layout[y][x] = 'E'
                elif (x > (end_inset + offset)):
                    room_layout[y][x] = 'E'

            if (floor_size < circle_size):
                if y < start_inset:
                    floor_size += 2
                    offset += 1
                elif y > end_inset:
                    floor_size -= 2
                    offset -= 1
            elif (floor_size == circle_size):
                if y >= end_inset:
                    floor_size -= 2
                    offset -= 1

        if donut:
            pass

        #print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in room_layout]))

        prefab = Prefab(room_layout)

        return prefab

    def curved_side_shaped_room(self):

        corner_to_round = randint(1,2)

        top_left = False
        top_right = False
        bottom_left = False
        bottom_right = False

        min_height = 7
        max_height = 15
        min_width = 7
        max_height = 15

        if corner_to_round == 1:
            top_left = True
        elif corner_to_round == 2:
            top_right = True
        elif corner_to_round == 3:
            bottom_left = True
        elif corner_to_round == 4:
            bottom_right = True

        floor_size = 2

        height = randrange(min_height, max_height, 2)
        width = randrange(min_height, max_height, 2)

        room_layout = [[i for i in range(width)] for i in range(height)]

        start_inset = width - floor_size
        end_inset = width - start_inset

        offset = 0

        print("Start inset: " + str(start_inset))
        print("End inset: " + str(end_inset))
        for y in range(height):
            for x in range(width):
                if (top_left or bottom_left) and (x < (start_inset - offset)):
                    room_layout[y][x] = 'E'
                elif (top_right or bottom_right) and (x > (end_inset + offset)):
                    room_layout[y][x] = 'E'

            if (floor_size < width):
                if y < start_inset:
                    floor_size += 1
                    offset += 1
                elif y >= (start_inset + floor_size):
                    floor_size -= 1
                    offset -= 1
            elif (floor_size == width):
                pass
                #if y >= end_inset:
                #    floor_size -= 2
                #    offset -= 1

        print('===================================================')
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in room_layout]))

        prefab = Prefab(room_layout)

        return prefab
'''
import numpy as np
m = np.array([[1,2,3],
         [2,3,3],
         [5,4,3]])

def rotate_matrix(mat):
    return np.rot90(mat)
'''
