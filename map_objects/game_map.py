import tcod
from random import choice, sample, randint, getrandbits, shuffle

import bestiary
import quest

from components.stairs import Stairs

from entities.entity import Entity
from entities.character import Character

from etc.colors import COLORS
from etc.configuration import CONFIG

from map_objects.np_level_generation import arena, levelOneGenerator, levelGenerator, bossLevelGenerator
from map_objects.point import Point
from map_objects.np_level_map import LevelMap

from etc.enum import RenderOrder, RoutingOptions, Species, Tiles

from utils.random_utils import from_dungeon_level, random_choice_from_dict

class GameMap:
    def __init__(self, dungeon_level=1):
        self.dungeon_level = dungeon_level
        self.current_level = None

    def make_map(self, map_width, map_height, player):
        '''
        valid = False
        count = 1
        while not valid:
            print('Map Attempt: ' + str(count))
            dm = levelGenerator(map_width, map_height)

            valid = dm.validateMap()

            if valid:
                self.current_level = LevelMap(dm.grid)
            else:
                valid = self.make_map()
                count += 1
        '''
        dm = bossLevelGenerator(map_width, map_height)
        self.current_level = LevelMap(dm.grid)
        self.test_popluate_map(player)

        #self.current_level = self.level_generator(map_width, map_height)
        #self.current_level.dungeon_level = self.dungeon_level

        #self.level_generic(player)
        return

        boss_chance = randint(0,3) + self.dungeon_level

        if (self.dungeon_level == 1):
            self.current_level = level_one_generator(map_width, map_height)
        else:
            if (boss_chance >= 6):
                self.current_level = level_boss_generator(map_width, map_height)
            else:
                self.current_level = level_generator(map_width, map_height)

        self.current_level.dungeon_level = self.dungeon_level

        if (self.dungeon_level == 1):
            self.level_one(player)
        else:
            if (boss_chance >= 6):
                self.level_boss(player)
            else:
                self.level_generic(player)

    def test_popluate_map(self, player):

        stairoptions = self.current_level.tiles_of_type(Tiles.STAIRSFLOOR)
        print(stairoptions)

        x = stairoptions[0][0]
        y = stairoptions[1][0]
        player.set_point(Point(x,y))
        self.current_level.add_entity(player)

        x = stairoptions[0][1]
        y = stairoptions[1][1]
        self.down_stairs = Entity(Point(x,y), '>', 'Stairs', COLORS.get('stairs'),
                                    render_order=RenderOrder.STAIRS)
        self.down_stairs.add_component(Stairs(self.dungeon_level + 1), "stairs")
        self.current_level.add_entity(self.down_stairs)

        #for i in range(5):
        #    point = self.current_level.find_random_open_position([], room = room)
        #    egg = bestiary.generate_creature(Species.EGG, self.dungeon_level, player.level.current_level, point)
        #    self.current_level.add_entity(egg)

        #point = self.current_level.find_random_open_position([], room = self.current_level.floor.rooms[0])
        #warlord = bestiary.warlord(point)
        #warlord.ai.set_target(player)
        #self.current_level.add_entity(warlord)

        #necromancer = bestiary.necromancer(point)
        #necromancer.ai.set_target(player)
        #self.current_level.add_entity(necromancer)

        '''
        for i in range(3):
            pt = self.current_level.find_random_open_position([], room = room)
            npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level, pt)
            bestiary.upgrade_npc(npc)
            self.current_level.add_entity(npc)

        #Add npcs and items
        for room in self.current_level.floor.rooms:
            self.place_npc(room, player)
            self.place_object(room)

        for i in range(1):
            room = self.current_level.floor.rooms[-1]
            point = self.current_level.find_random_open_position([], room=room)
            bestiary.place_chest(point, self.current_level, player)


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
        point = self.current_level.find_random_open_position([], room = room)
        self.down_stairs = Entity(point, '>', 'Stairs', COLORS.get('stairs'),
                                    render_order=RenderOrder.STAIRS)
        self.down_stairs.add_component(Stairs(self.dungeon_level + 1), "stairs")
        self.current_level.add_entity(self.down_stairs)
        self.current_level.downward_stairs_position = (self.down_stairs.x, self.down_stairs.y)

        room = self.current_level.floor.rooms[0]
        point = self.current_level.find_random_open_position([], room = room)
        player.set_point(point)
        self.current_level.add_entity(player)

        point = self.current_level.find_random_open_position([RoutingOptions.AVOID_STAIRS], room = room)
        npc = bestiary.bountyhunter(point)

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

        point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                RoutingOptions.AVOID_DOORS,
                                                                RoutingOptions.AVOID_FLOORS,
                                                                RoutingOptions.AVOID_STAIRS])
        bestiary.place_chest(point, self.current_level, player)

        num_rooms = len(self.current_level.floor.rooms)
        for room in self.current_level.floor.rooms[1:num_rooms]:
            num_npcs = randint(0, 2)

            for i in range(num_npcs):
                npc = bestiary.generate_npc(Species.GOBLIN, self.dungeon_level, player.level.current_level)
                point = self.current_level.find_random_open_position(npc.movement.routing_avoid, room=room)
                npc.set_point(point)
                self.current_level.add_entity(npc)

        room = choice(self.current_level.floor.rooms[1:num_rooms])
        point = self.current_level.find_random_open_position([], room=room)
        bestiary.place_chest(point, self.current_level, player)

    def level_generic(self, player):
        self.down_stairs = Entity(self.current_level.floor.rooms[-1].center_tile(), '>', 'Down Stairs',
                                        COLORS.get('stairs'), render_order=RenderOrder.STAIRS)
        self.down_stairs.add_component(Stairs(self.dungeon_level + 1), "stairs")

        self.up_stairs = Entity(self.current_level.floor.rooms[-1].center_tile(), '<', 'Up Stairs',
                                    COLORS.get('stairs'), render_order=RenderOrder.STAIRS)
        self.up_stairs.add_component(Stairs(self.dungeon_level - 1), "stairs")

        self.current_level.add_entity(self.down_stairs)
        self.current_level.add_entity(self.up_stairs)

        self.current_level.downward_stairs_position = (self.down_stairs.x, self.down_stairs.y)
        self.current_level.upward_stairs_position = (self.up_stairs.x, self.up_stairs.y)

        player.set_point(self.up_stairs)
        self.current_level.add_entity(player)

        if len(self.current_level.floor.caves) > 0:
            self.place_creatures(player)

    def level_boss(self, player):
        room = self.current_level.floor.rooms[0]
        warlord = bestiary.warlord(Point(room.x+5, room.y + 2))
        self.current_level.add_entity(warlord)

        room = self.current_level.floor.rooms[-1]
        self.up_stairs = Entity(self.current_level.floor.rooms[-1].center_tile(), '<', 'Up Stairs',
                                    COLORS.get('stairs'), render_order=RenderOrder.STAIRS)
        self.up_stairs.add_component(Stairs(self.dungeon_level - 1), "stairs")
        self.current_level.add_entity(self.up_stairs)

        player.set_point(self.up_stairs.point)

        npc = bestiary.bountyhunter()
        npc.point = self.current_level.find_random_open_position(npc.movement.routing_avoid, room=room)

        q = quest.kill_warlord()
        npc.questgiver.add_quest(q)
        self.current_level.add_entity(npc)

        #Add npcs and items
        for room in self.current_level.floor.rooms:
            self.place_npc(room, player)
            self.place_object(room)

    def place_creatures(self, player):
        npc_chances = {}
        npc_chances[Species.RAT] = from_dungeon_level([[95, 1], [95, 2], [30, 3], [15, 4], [10, 5], [5, 6]], self.dungeon_level)
        npc_chances[Species.SNAKE] = from_dungeon_level([[95, 1], [4,2], [65, 3], [65, 4], [50, 5], [45, 6]], self.dungeon_level)
        npc_chances[Species.EGG] = from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances[Species.RATNEST] = from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)
        npc_chances[Species.BAT] = from_dungeon_level([[95, 1], [1,3], [5, 3], [20, 4], [40, 5], [60, 6]], self.dungeon_level)

        max_npcs = len(self.current_level.floor.caves) // 100

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

            point = self.current_level.find_random_open_position([RoutingOptions.AVOID_STAIRS], room=room)

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

    def next_floor(self, player):
        self.dungeon_level += 1

        self.create_floor(player)

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

    def level_one_goblin(self):
        point = self.current_level.find_random_open_position([RoutingOptions.AVOID_CORRIDORS,
                                                                RoutingOptions.AVOID_DOORS,
                                                                RoutingOptions.AVOID_FLOORS,
                                                                RoutingOptions.AVOID_STAIRS,
                                                                RoutingOptions.AVOID_FOV])

        self.current_level.add_entity(bestiary.generate_npc(Species.GOBLIN, 1, 1, point))
