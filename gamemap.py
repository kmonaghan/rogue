import libtcodpy as libtcod
import pc
import baseclasses
import equipment
import characterclass
import messageconsole
import random
import bestiary
import ai

from map_objects.rect import Rect
from map_objects.room import Room
from map_objects.tile import Tile
from map_objects.altbsptree import AltBSPTree
from map_objects.bsptree import BSPTree
from map_objects.cellularautomata import CellularAutomata
from map_objects.mazewithrooms import MazeWithRooms
from map_objects.map_utils import is_blocked

import game_state

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40

MAX_MAP_WIDTH = 80
MAX_MAP_HEIGHT = 40

dungeon_level = 1

stairs = None

def make_bsp():
    global bsp_rooms, MAP_HEIGHT, MAP_WIDTH

    game_state.objects = []

    if (dungeon_level <= 2):
        MAP_HEIGHT = (MAX_MAP_HEIGHT / 3) * 2
        MAP_WIDTH = (MAX_MAP_WIDTH / 3) * 2
    else:
        MAP_HEIGHT = MAX_MAP_HEIGHT
        MAP_WIDTH = MAX_MAP_WIDTH

    print "Generating Map sized: " + str(MAP_WIDTH) + " x " + str(MAP_HEIGHT)

    if (dungeon_level <= 2):
        generator = AltBSPTree()
    elif (dungeon_level <= 4):
        generator = MazeWithRooms()

    #generator = BSPTree()
    #generator = CellularAutomata()

    game_state.map = generator.generateLevel(MAP_WIDTH, MAP_HEIGHT)

    print "Map size: " + str(len(game_state.map)) + " x " + str(len(game_state.map[0]))
    bsp_rooms = generator.rooms

    print "Number of rooms: " + str(len(bsp_rooms))

    popluate_map()

def popluate_map():
    global stairs, bsp_rooms

    room = random.choice(bsp_rooms)
    bsp_rooms.remove(room)
    point = room.random_tile()

    if (dungeon_level <= 4):
        stairs = baseclasses.Object(point, '<', 'stairs', libtcod.white, always_visible=True)
        game_state.objects.append(stairs)
        stairs.send_to_back()
    else:
        warlord = bestiary.warlord(point)
        game_state.objects.append(warlord)

    #Random room for player start
    room = random.choice(bsp_rooms)
    bsp_rooms.remove(room)
    point = room.random_tile()
    pc.player.x = point.x
    pc.player.y = point.y
    game_state.objects.append(pc.player)

    point = room.random_tile()
    npc = bestiary.bountyhunter(point)
    game_state.objects.append(npc)


    #Add npcs and items
    for room in bsp_rooms:
        place_objects(room)

    if (len(bsp_rooms) > 4):
        num_to_select = 4                           # set the number to select here.
        list_of_random_items = random.sample(bsp_rooms, num_to_select)

        room = list_of_random_items[0]
        point = room.random_tile()
        npc = bestiary.goblin(point)
        npc.ai = ai.WanderingNPC(list_of_random_items, npc.ai)
        npc.ai.owner = npc
        bestiary.upgrade_npc(npc)
        game_state.objects.append(npc)

def place_objects(room):
    #this is where we decide the chance of each npc or item appearing.

    #maximum number of npcs per room
    max_npcs = baseclasses.from_dungeon_level([[2, 1], [3, 3], [5, 4]])

    #chance of each npc
    npc_chances = {}
    npc_chances['goblin'] = baseclasses.from_dungeon_level([[95, 1], [30, 2], [15, 3], [10, 4], [5, 5]])
    npc_chances['orc'] = baseclasses.from_dungeon_level([[4,1], [65, 2], [65, 3], [50, 4], [45, 5]])
    npc_chances['troll'] = baseclasses.from_dungeon_level([[1,1], [5, 2], [20, 3], [40, 4], [60, 5]])

    #maximum number of items per room
    max_items = baseclasses.from_dungeon_level([[2, 1], [3, 4]])

    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['potion'] = 25  #healing potion always shows up, even if all other items have 0 chance
    item_chances['scroll'] = baseclasses.from_dungeon_level([[25, 2]])
    item_chances['weapon'] = 25
    item_chances['armour'] = 25

    #choose random number of npcs
    num_npcs = libtcod.random_get_int(0, 0, max_npcs)

    for i in range(num_npcs):
        #choose random spot for this npc
        point = room.random_tile()

        #only place it if the tile is not blocked
        if not is_blocked(point):
            choice = baseclasses.random_choice(npc_chances)
            if choice == 'orc':
                npc = bestiary.orc(point)
            elif choice == 'troll':
                npc = bestiary.troll(point)
            elif choice == 'goblin':
                npc = bestiary.goblin(point)

            game_state.objects.append(npc)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose random spot for this item
        point = room.random_tile()

        #only place it if the tile is not blocked
        if not is_blocked(point):
            choice = baseclasses.random_choice(item_chances)
            if choice == 'potion':
                item = equipment.random_potion(point)
            elif choice == 'scroll':
                item = equipment.random_scroll(point)
            elif choice == 'weapon':
                item = equipment.random_weapon(point)
            elif choice == 'armour':
                item = equipment.random_armour(point)

            game_state.objects.append(item)
            item.send_to_back()  #items appear below other objects
            item.always_visible = True  #items are visible even out-of-FOV, if in an explored area

def boss_room(point):
    room_map = ["#########",
                "###...###",
                "##.....##",
                "#.......#",
                "#.#...#.#",
                "#.......#",
                "#.#...#.#",
                "#.......#",
                "#.#...#.#",
                "#.......#",
                "####.####"]
