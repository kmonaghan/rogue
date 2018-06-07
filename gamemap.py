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
from map_objects.map_utils import is_blocked

import game_state

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40

MAX_MAP_WIDTH = 80
MAX_MAP_HEIGHT = 40

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

DEPTH = 10
MIN_SIZE = 5
#set this to tru to have a full map
FULL_ROOMS = False

dungeon_level = 1

stairs = None

def traverse_node(node, dat):
    global bsp_rooms

    #Create rooms
    if libtcod.bsp_is_leaf(node):
        minx = node.x + 1
        maxx = node.x + node.w - 1
        miny = node.y + 1
        maxy = node.y + node.h - 1

        if maxx == MAP_WIDTH - 1:
            maxx -= 1
        if maxy == MAP_HEIGHT - 1:
            maxy -= 1

        #If it's False the rooms sizes are random, else the rooms are filled to the node's size
        if FULL_ROOMS == False:
            minx = libtcod.random_get_int(None, minx, maxx - MIN_SIZE + 1)
            miny = libtcod.random_get_int(None, miny, maxy - MIN_SIZE + 1)
            maxx = libtcod.random_get_int(None, minx + MIN_SIZE - 2, maxx)
            maxy = libtcod.random_get_int(None, miny + MIN_SIZE - 2, maxy)

        room = Room(minx, miny, maxx, maxy)
        node.x = minx
        node.y = miny
        node.w = maxx-minx + 1
        node.h = maxy-miny + 1

        #Dig room
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                game_state.map[x][y].blocked = False
                game_state.map[x][y].block_sight = False

        bsp_rooms.append(room)

    #Create corridors
    else:
        left = libtcod.bsp_left(node)
        right = libtcod.bsp_right(node)
        node.x = min(left.x, right.x)
        node.y = min(left.y, right.y)
        node.w = max(left.x + left.w, right.x + right.w) - node.x
        node.h = max(left.y + left.h, right.y + right.h) - node.y
        if node.horizontal:
            if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
                x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
                x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
                y = libtcod.random_get_int(None, left.y + left.h, right.y)
                vline_up(game_state.map, x1, y - 1)
                hline(game_state.map, x1, y, x2)
                vline_down(game_state.map, x2, y + 1)

            else:
                minx = max(left.x, right.x)
                maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                x = libtcod.random_get_int(None, minx, maxx)

                # catch out-of-bounds attempts
                while x > MAP_WIDTH - 1:
                        x -= 1

                vline_down(game_state.map, x, right.y)
                vline_up(game_state.map, x, right.y - 1)

        else:
            if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
                y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
                y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
                x = libtcod.random_get_int(None, left.x + left.w, right.x)
                hline_left(game_state.map, x - 1, y1)
                vline(game_state.map, x, y1, y2)
                hline_right(game_state.map, x + 1, y2)
            else:
                miny = max(left.y, right.y)
                maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                y = libtcod.random_get_int(None, miny, maxy)

                # catch out-of-bounds attempts
                while y > MAP_HEIGHT - 1:
                         y -= 1

                hline_left(game_state.map, right.x - 1, y)
                hline_right(game_state.map, right.x, y)

    return True

def make_bsp():
    global stairs, bsp_rooms, MAP_HEIGHT, MAP_WIDTH

    game_state.objects = [pc.player]

    if (dungeon_level <= 2):
        MAP_HEIGHT = (MAX_MAP_HEIGHT / 3) * 2
        MAP_WIDTH = (MAX_MAP_WIDTH / 3) * 2
    else:
        MAP_HEIGHT = MAX_MAP_HEIGHT
        MAP_WIDTH = MAX_MAP_WIDTH

    game_state.map = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    #Empty global list for storing room coordinates
    bsp_rooms = []

    #New root node
    bsp = libtcod.bsp_new_with_size(0, 0, MAP_WIDTH, MAP_HEIGHT)

    #Split into nodes
    libtcod.bsp_split_recursive(bsp, 0, DEPTH, MIN_SIZE + 1, MIN_SIZE + 1, 1.5, 1.5)

    #Traverse the nodes and create rooms
    libtcod.bsp_traverse_inverted_level_order(bsp, traverse_node)

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

    point = room.random_tile()
    npc = bestiary.bountyhunter(point)
    npc.always_visible = True
    print "Bounty Hunter point: " + str(point.x) + ", " + str(point.y)
    game_state.objects.append(npc)

    print "map size: " + str(len(game_state.map))

    #Add npcs and items
    for room in bsp_rooms:
        place_objects(room)

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

def vline(map, x, y1, y2):
    if y1 > y2:
        y1,y2 = y2,y1

    for y in range(y1,y2+1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def vline_up(map, x, y):
    while y >= 0 and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        y -= 1

def vline_down(map, x, y):
    while y < MAP_HEIGHT and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        y += 1

def hline(map, x1, y, x2):
    if x1 > x2:
        x1,x2 = x2,x1
    for x in range(x1,x2+1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def hline_left(map, x, y):
    while x >= 0 and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        x -= 1

def hline_right(map, x, y):
    while x < MAP_WIDTH and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        x += 1

def boos_room(point):
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
