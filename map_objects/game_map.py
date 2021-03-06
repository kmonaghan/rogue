import logging
import tcod
import numpy as np
from random import choice, sample, randint, getrandbits, shuffle

import bestiary
import buildings
from quest_generation import generate_quest_chain

from components.stairs import Stairs
from components.locked import Locked

from entities.entity import Entity
from entities.character import Character

from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.exceptions import MapError, MapGenerationFailedError

from map_objects.np_dungeonGeneration import cellular_map
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
        #player.set_point(Point(10,10))

        self.generate_layout(map_width, map_height, player)
        self.populate_map(player)

    def generate_layout(self, map_width, map_height, player):
        #return self.generate_test_layout(map_width, map_height, player)

        attempts = 0

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
                logging.info(f"===Map generation failed=== {e}")
                attempts = attempts + 1
                dm = None

        if not dm:
            raise MapGenerationFailedError

        self.current_level = LevelMap(dm.grid, dm.rooms)
        self.current_level.dungeon_level = self.dungeon_level

    def generate_test_layout(self, map_width, map_height, player):
        attempts = 0

        while attempts < CONFIG.get('map_generation_attempts'):
            try:
                dm = arena(map_width, map_height)
                #dm = levelGenerator(map_width, map_height, player.x, player.y)

                break
            except MapError as e:
                logging.info(f"===Map generation failed=== {e}")
                attempts = attempts + 1
                dm = None

        if not dm:
            raise MapGenerationFailedError

        self.current_level = LevelMap(dm.grid, dm.rooms)
        self.current_level.dungeon_level = self.dungeon_level

    def populate_map(self, player):
        self.place_stairs()
        self.place_doors()

        #return self.test_popluate_map(player)

        player.set_point(self.up_stairs.point)
        self.current_level.add_entity(player)

        self.fill_prefab(player)

        if (self.dungeon_level == 1):
            self.level_one(player)
        else:
            self.level_generic(player)

    def test_popluate_map(self, player):
        point = self.current_level.find_random_open_position()
        item = equipment.healing_potion(Point(27,27))
        self.current_level.add_entity(item)

        item2 = equipment.healing_potion(player.point)
        self.current_level.add_entity(item2)

        #cube = bestiary.gelatinous_cube(item.point)
        #self.current_level.add_entity(cube)

        #npc = bestiary.generate_npc(Species.TROLL, self.dungeon_level)
        #npc.set_point(Point(26,26))
        #self.current_level.add_entity(npc)

        npc = bestiary.spawn_point(Point(26,26), Species.TROLL)
        self.current_level.add_entity(npc)
        self.place_doors()

    def place_doors(self):
        doors_tiles = self.current_level.doors

        current_door_tuples = tuple(zip(doors_tiles[0],doors_tiles[1]))

        for x,y in current_door_tuples:
            door = buildings.door(Point(x,y))
            self.current_level.add_entity(door)

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
        self.add_bounty_hunter()

        #Snakes and Rats
        for _ in range(10):
            snake = bestiary.generate_creature(Species.SNAKE, self.dungeon_level)
            point = self.current_level.find_random_open_position(snake.movement.routing_avoid)
            snake.set_point(point)
            self.current_level.add_entity(snake)

            rat = bestiary.generate_creature(Species.RAT, self.dungeon_level)
            point = self.current_level.find_random_open_position(rat.movement.routing_avoid)
            rat.set_point(point)
            self.current_level.add_entity(rat)

        for _ in range(6):
            nest = bestiary.generate_creature(Species.RATNEST, self.dungeon_level)
            point = self.current_level.find_random_open_position(nest.movement.routing_avoid)
            nest.set_point(point)
            self.current_level.add_entity(nest)

        roosts = randint(0, 3)

        for _ in range(roosts):
            nest = bestiary.generate_creature(Species.BATROOST, self.dungeon_level)
            point = self.current_level.find_random_open_position(nest.movement.routing_avoid)
            nest.set_point(point)
            self.current_level.add_entity(nest)

        hives = randint(0, 3)

        for _ in range(hives):
            nest = bestiary.generate_creature(Species.HORNETNEST, self.dungeon_level)
            point = self.current_level.find_random_open_position(nest.movement.routing_avoid)
            nest.set_point(point)
            self.current_level.add_entity(nest)

    def level_generic(self, player):
        if len(self.current_level.caves[0]) > 0:
            self.place_creatures(player)
        if len(self.current_level.floors[0]) > 0:
            self.place_npc(player)

        if len(self.current_level.corridors[0]) > 0:
            max_cubes = len(self.current_level.corridors[0]) // 75

            num_cubes = randint(0, max_cubes)

            for _ in range(0, num_cubes):
                cube = bestiary.gelatinous_cube()
                point = self.current_level.find_random_open_position(cube.movement.routing_avoid)
                cube.set_point(point)
                self.current_level.add_entity(cube)

    def place_creatures(self, player):
        npc_chances = {}
        npc_chances[Species.RAT] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.SNAKE] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.EGG] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.RATNEST] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.BAT] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.BATROOST] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.INSECT] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.HORNETNEST] = from_dungeon_level([[95, 1]], self.dungeon_level)

        max_npcs = len(self.current_level.caves[0]) // 15
        min_npcs = max(1, max_npcs // 4)
        num_npcs = randint(min_npcs, max_npcs)

        logging.info (f"Max creatures: {max_npcs}, number of creatures: {num_npcs}")

        for _ in range(num_npcs):
            #choose random spot for this npc
            creature_choice = random_choice_from_dict(npc_chances)

            npc = bestiary.generate_creature(creature_choice, self.dungeon_level)
            avoid = npc.movement.routing_avoid.copy()
            avoid.extend([Tiles.CORRIDOR_FLOOR, Tiles.DOOR, Tiles.STAIRS_FLOOR])
            point = self.current_level.find_random_open_position(avoid)
            npc.set_point(point)
            self.current_level.add_entity(npc)

    def place_npc(self, player):
        #this is where we decide the chance of each npc appearing.

        #chance of each npc
        npc_chances = {}
        npc_chances[Species.GOBLIN] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.ORC] = from_dungeon_level([[95, 1]], self.dungeon_level)
        npc_chances[Species.TROLL] = from_dungeon_level([[95, 1]], self.dungeon_level)

        max_npcs = len(self.current_level.floors[0]) // 15
        min_npcs = max(1, max_npcs // 4)
        num_npcs = randint(min_npcs, max_npcs)

        logging.info (f"Min NPCs: {min_npcs}, Max NPCx: {max_npcs}, number of NPCs: {num_npcs}")

        for _ in range(num_npcs):
            choice = random_choice_from_dict(npc_chances)
            npc = bestiary.generate_npc(choice, self.dungeon_level)
            avoid = npc.movement.routing_avoid.copy()
            avoid.extend([Tiles.CAVERN_FLOOR, Tiles.FUNGAL_CAVERN_FLOOR, Tiles.CORRIDOR_FLOOR, Tiles.DOOR, Tiles.STAIRS_FLOOR])
            point = self.current_level.find_random_open_position(avoid)
            npc.set_point(point)
            npc.ai.set_target(player)
            self.current_level.add_entity(npc)

    def fill_prefab(self, player):
        npc = None
        room_name = None
        for room in self.current_level.rooms:
            if room.name == "treasure_room":
                point = Point(room.spawnpoints[0][0] + room.x, room.spawnpoints[0][1] + room.y)
                bestiary.place_chest(point, self.current_level, player)

                all_doors = self.current_level.find_tile_within_room(room, Tiles.DOOR)

                door_entities = self.current_level.entities.get_entities_in_position((all_doors[0][0], all_doors[1][0]))
                key = buildings.make_lockable(door_entities[0])
                self.current_level.update_entity_position(door_entities[0])
                point = self.current_level.find_random_open_position()
                key.set_point(point)
                self.current_level.add_entity(key)
            elif room.name == "barracks":
                point = Point(room.spawnpoints[0][0] + room.x, room.spawnpoints[0][1] + room.y)
                npc = bestiary.captain(point, self.dungeon_level)
                npc.ai.set_target(player)
                self.current_level.add_entity(npc)
                room_name = "the barracks"
            elif room.name == "necromancer_lair":
                point = Point(room.spawnpoints[0][0] + room.x, room.spawnpoints[0][1] + room.y)
                npc = bestiary.necromancer(point, self.dungeon_level)
                npc.ai.set_target(player)
                self.current_level.add_entity(npc)
                room_name = "his labratory of death"
            elif room.name == "vampire_lair":
                spawn = choice(room.spawnpoints)
                point = Point(spawn[0] + room.x, spawn[1] + room.y)
                npc = bestiary.generate_random_vampire(point, self.dungeon_level)
                npc.ai.set_target(player)
                self.current_level.add_entity(npc)
                room_name = "his lair"
            elif room.name == "prison_block":
                spawn = choice(room.spawnpoints)
                point = Point(spawn[0] + room.x, spawn[1] + room.y)
                npc = bestiary.jailor(point, self.dungeon_level)
                npc.ai.set_target(player)
                self.current_level.add_entity(npc)
                room_name = "prison block"
            elif room.name == "boss_room":
                point = Point(room.spawnpoints[0][0] + room.x, room.spawnpoints[0][1] + room.y)
                npc = bestiary.warlord(point, self.dungeon_level)
                npc.ai.set_target(player)
                self.current_level.add_entity(npc)
                room_name = room.name

        if npc:
            logging.info(f"Adding quest for: {npc.name}")
            self.add_bounty_hunter(npc, room_name = room_name)
        else:
            logging.info("NO QUEST!")

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

    def add_bounty_hunter(self, target_npc = None, room_name = None):
        entrance = find(lambda room: room.name == 'entrance', self.current_level.rooms)
        point = self.current_level.find_random_open_position([Tiles.STAIRS_FLOOR, Tiles.DOOR], room=entrance)

        npc = bestiary.bountyhunter(point)

        npc.questgiver.add_quest(generate_quest_chain(self, npc, room_name))
        self.current_level.add_entity(npc)
