import tcod
import numpy as np
from random import choice, sample, randint, getrandbits, shuffle

import bestiary
import buildings
import quest

from components.stairs import Stairs

from entities.entity import Entity
from entities.character import Character

from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.exceptions import MapError, MapGenerationFailedError

from map_objects.np_level_generation import arena, levelOneGenerator, levelGenerator, bossLevelGenerator
from map_objects.point import Point
from map_objects.np_level_map import LevelMap

from etc.enum import RenderOrder, RoutingOptions, Species, StairOption, Tiles

from utils.random_utils import from_dungeon_level, random_choice_from_dict
from utils.utils import find

from utils.utils import matprint

import equipment

class GameMap:
    def __init__(self, dungeon_level=1):
        self.dungeon_level = dungeon_level
        self.current_level = None
        self.levels = []

    def make_map(self, map_width, map_height, player):
        dm = None

        attempts = 0
        '''
        while attempts < CONFIG.get('map_generation_attempts'):
            try:
                dm = arena(map_width, map_height)
                break
            except MapError as e:
                print(f"===Map generation failed=== {e}")
                attempts = attempts + 1
                dm = None

        if not dm:
            raise MapGenerationFailedError

        self.current_level = LevelMap(dm.grid, dm.rooms)
        self.current_level.dungeon_level = self.dungeon_level

        point = self.current_level.find_random_open_position()
        player.set_point(point)

        self.current_level.add_entity(player)
        self.test_popluate_map(player)

        return
        '''
        boss_chance = randint(0,3) + self.dungeon_level

        while attempts < CONFIG.get('map_generation_attempts'):
            try:
                if (self.dungeon_level == 1):
                    dm = levelOneGenerator(map_width, map_height)
                else:
                    if (boss_chance >= 6):
                        dm = bossLevelGenerator(map_width, map_height, player.x, player.y)
                    else:
                        dm = levelGenerator(map_width, map_height, player.x, player.y)
                break
            except MapError as e:
                print(f"===Map generation failed=== {e}")
                attempts = attempts + 1
                dm = None

        if not dm:
            raise MapGenerationFailedError

        self.current_level = LevelMap(dm.grid, dm.rooms)
        self.current_level.dungeon_level = self.dungeon_level

        self.place_stairs()
        self.place_doors()

        player.set_point(self.up_stairs.point)

        self.current_level.add_entity(player)

        if (self.dungeon_level == 1):
            self.level_one(player)
        else:
            if (boss_chance >= 6):
                self.levelBoss(player)
            else:
                self.levelGeneric(player)

        self.fill_prefab(player)

    def test_popluate_map(self, player):
        #point = self.current_level.find_random_open_position()
        #warlord = bestiary.warlord(point)
        #warlord.ai.set_target(player)
        #self.current_level.add_entity(warlord)

        prison_block = find(lambda room: room.name == 'prison_block', self.current_level.rooms)

        npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level)
        point = self.current_level.find_random_open_position(npc.movement.routing_avoid)
        npc.set_point(point)
        bestiary.poison_npc(npc)
        self.current_level.add_entity(npc)

        # if prison_block:
        #     for x,y in prison_block.spawnpoints:
        #         npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level)
        #         npc.set_point(Point(prison_block.x + x, prison_block.y + y))
        #         npc.ai.set_target(player)
        #         self.current_level.add_entity(npc)

        #Snakes and Rats
        # for i in range(1):
        #     npc = bestiary.generate_creature(Species.SNAKE, self.dungeon_level, player.level.current_level)
        #     point = self.current_level.find_random_open_position(npc.movement.routing_avoid)
        #     npc.set_point(point)
        #     npc.ai.set_target(player)
        #     self.current_level.add_entity(npc)

        '''
        for i in range(5):
            npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level)
            point = self.current_level.find_random_open_position(npc.movement.routing_avoid)
            npc.set_point(point)
            npc.ai.set_target(player)
            self.current_level.add_entity(npc)

        point = self.current_level.find_random_open_position()
        #Potions, scrolls and rings
        potion = equipment.healing_potion(point)
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

        point = self.current_level.find_random_open_position()
        potion2 = equipment.power_potion(point)
        self.current_level.add_entity(potion2)

        point = self.current_level.find_random_open_position()
        potion3 = equipment.defence_potion(point)
        self.current_level.add_entity(potion3)

        point = self.current_level.find_random_open_position()
        scroll5 = equipment.identify_scroll(player.point)
        self.current_level.add_entity(scroll5)

        self.place_doors()

    def place_doors(self):
        doors_tiles = self.current_level.doors

        current_door_tuples = tuple(zip(doors_tiles[0],doors_tiles[1]))

        print(current_door_tuples)

        for x,y in current_door_tuples:
            door = buildings.door(Point(x,y))
            self.current_level.add_entity(door)

            point = self.current_level.find_random_open_position()
            key = equipment.key(point, door)
            self.current_level.add_entity(key)

    def place_stairs(self):
        exit = find(lambda room: room.name == 'exit', self.current_level.rooms)

        if (exit):
            x,y = exit.center

            self.down_stairs = Entity(Point(x,y), '>', 'Stairs', COLORS.get('stairs'),
                                                render_order=RenderOrder.STAIRS, always_visible=True)
            self.down_stairs.add_component(Stairs(self.dungeon_level + 1), "stairs")

            self.current_level.add_entity(self.down_stairs)

        entrance = find(lambda room: room.name == 'entrance', self.current_level.rooms)

        if (entrance):
            x,y = entrance.center

            self.up_stairs = Entity(Point(x,y), '<', 'Stairs', COLORS.get('stairs'),
                                                render_order=RenderOrder.STAIRS, always_visible=True)
            self.up_stairs.add_component(Stairs(self.dungeon_level - 1), "stairs")

            self.current_level.add_entity(self.up_stairs)

    def level_one(self, player):
        #point = self.current_level.find_random_open_position([Tiles.STAIRS_FLOOR], room = room)
        npc = bestiary.bountyhunter(Point(player.x-1, player.y-1))

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
            snake = bestiary.generate_creature(Species.SNAKE, self.dungeon_level, player.level.current_level)
            point = self.current_level.find_random_open_position(snake.movement.routing_avoid)
            snake.set_point(point)
            self.current_level.add_entity(snake)

            rat = bestiary.generate_creature(Species.RAT, self.dungeon_level, player.level.current_level)
            point = self.current_level.find_random_open_position(rat.movement.routing_avoid)
            rat.set_point(point)
            self.current_level.add_entity(rat)

        for i in range(6):
            nest = bestiary.generate_creature(Species.RATNEST, self.dungeon_level, player.level.current_level)
            point = self.current_level.find_random_open_position(nest.movement.routing_avoid)
            nest.set_point(point)
            self.current_level.add_entity(nest)

    def levelGeneric(self, player):
        if len(self.current_level.caves) > 0:
            self.place_creatures(player)

    def levelBoss(self, player):
        npc = bestiary.bountyhunter(Point(player.x-1,player.y-1))

        q = quest.kill_warlord()
        npc.questgiver.add_quest(q)
        self.current_level.add_entity(npc)

        point = self.current_level.find_random_open_position(room=self.current_level.rooms[1])
        warlord = bestiary.warlord(point)
        warlord.ai.set_target(player)
        self.current_level.add_entity(warlord)

    def place_creatures(self, player):
        npc_chances = {}
        npc_chances[Species.RAT] = from_dungeon_level([[95, 1], [95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances[Species.SNAKE] = from_dungeon_level([[95, 1], [4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances[Species.EGG] = from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances[Species.RATNEST] = from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances[Species.BAT] = from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

        max_npcs = len(self.current_level.caves) // 100

        num_npcs = randint(1, max_npcs)

        print (f"Max NPCs: {max_npcs}, number of NPCs: {num_npcs}")

        for i in range(num_npcs):
            #choose random spot for this npc
            creature_choice = random_choice_from_dict(npc_chances)

            npc = bestiary.generate_creature(creature_choice, self.dungeon_level, player.level.current_level)
            point = self.current_level.find_random_open_position(npc.movement.routing_avoid)
            npc.set_point(point)
            self.current_level.add_entity(npc)

    def place_npc(self, room, player):
        #this is where we decide the chance of each npc or item appearing.

        #maximum number of npcs per room
        max_npcs = 4# from_dungeon_level([[1,2], [2, 2], [3, 4], [5, 5]], self.dungeon_level)

        #chance of each npc
        npc_chances = {}
        npc_chances[Species.GOBLIN] = from_dungeon_level([[95, 1],[95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances[Species.ORC] = from_dungeon_level([[95, 1],[4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances[Species.TROLL] = from_dungeon_level([[95, 1],[95, 2], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

        #choose random number of npcs
        num_npcs = randint(1, max_npcs)

        for i in range(num_npcs):
            choice = random_choice_from_dict(npc_chances)
            npc = bestiary.generate_npc(choice, self.dungeon_level, player.level.current_level)
            point = self.current_level.find_random_open_position(npc.movement.routing_avoid,
                                                                    room = room)
            npc.set_point(point)
            npc.ai.set_target(player)
            self.current_level.add_entity(npc)

    def fill_prefab(self, player):
        for room in self.current_level.rooms:
            if room.name == "treasure_room":
                print(room.spawnpoints)
                point = Point(room.spawnpoints[0][0] + room.x, room.spawnpoints[0][1] + room.y)
                bestiary.place_chest(point, self.current_level, player)

    def place_object(self, room):
        return
        #maximum number of items per room
        max_items = from_dungeon_level([[2, 1], [3, 4]], self.dungeon_level)

        #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        item_chances = {}
        item_chances['potion'] = 25  #healing potion always shows up, even if all other items have 0 chance
        item_chances['scroll'] = from_dungeon_level([[25, 2]], self.dungeon_level)
        item_chances['weapon'] = 25
        item_chances['armour'] = 25

        #choose random number of items
        num_items = randint(0, max_items)

        for i in range(num_items):
            #choose random spot for this item

            point = self.current_level.find_random_open_position([Tiles.STAIRS_FLOOR], room=room)

            choice = random_choice_from_dict(item_chances)
            if choice == 'potion':
                item = equipment.random_potion(point, self.dungeon_level)
            elif choice == 'scroll':
                item = equipment.random_scroll(point, self.dungeon_level)
            elif choice == 'weapon':
                item = equipment.random_weapon(point, self.dungeon_level)
            elif choice == 'armour':
                item = equipment.random_armour(point, self.dungeon_level)

            self.current_level.add_entity(item)

    def create_floor(self, player):
        self.down_stairs = None
        self.up_stairs = None

        self.make_map(CONFIG.get('map_width'), CONFIG.get('map_height'), player)

    def first_floor(self, player):
        self.dungeon_level = 1

        self.create_floor(player)

    def next_floor(self, player):
        #Need to reset pubsub

        self.dungeon_level += 1

        self.create_floor(player)

        if (self.dungeon_level > 1):
            player.health.heal(player.health.max_hp // 2)

    def previous_floor(self, player):
        #Need to reset pubsub
        self.dungeon_level -= 1

        self.create_floor(player)

    def check_for_stairs(self, x, y):
        if (self.down_stairs):
            if (self.down_stairs.x == x) and (self.down_stairs.y == y):
                return StairOption.GODOWN

        if (self.up_stairs):
            if (self.up_stairs.x == x) and (self.up_stairs.y == y):
                if self.dungeon_level == 1:
                    return StairOption.EXIT
                return StairOption.GOUP

        return StairOption.NOSTAIR

    def level_one_goblin(self):
        point = self.current_level.find_random_open_position([Tiles.CORRIDOR_FLOOR,
                                                                Tiles.DOOR,
                                                                Tiles.ROOM_FLOOR,
                                                                Tiles.STAIRS_FLOOR,
                                                                RoutingOptions.AVOID_FOV])

        self.current_level.add_entity(bestiary.generate_npc(Species.GOBLIN, 1, 1, point))
