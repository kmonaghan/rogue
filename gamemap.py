import libtcodpy as libtcod
import pc
import baseclasses
import equipment
import characterclass
import messageconsole
import random
import bestiary
import ai

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

DEPTH = 10
MIN_SIZE = 5
#set this to tru to have a full map
FULL_ROOMS = False

dungeon_level = 1

map = []
stairs = None

def traverse_node(node, dat):
    global map, bsp_rooms

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

        node.x = minx
        node.y = miny
        node.w = maxx-minx + 1
        node.h = maxy-miny + 1

        #Dig room
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                map[x][y].blocked = False
                map[x][y].block_sight = False

        #Add center coordinates to the list of rooms
        bsp_rooms.append(((minx + maxx) / 2, (miny + maxy) / 2))

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
                vline_up(map, x1, y - 1)
                hline(map, x1, y, x2)
                vline_down(map, x2, y + 1)

            else:
                minx = max(left.x, right.x)
                maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                x = libtcod.random_get_int(None, minx, maxx)

                # catch out-of-bounds attempts
                while x > MAP_WIDTH - 1:
                        x -= 1

                vline_down(map, x, right.y)
                vline_up(map, x, right.y - 1)

        else:
            if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
                y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
                y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
                x = libtcod.random_get_int(None, left.x + left.w, right.x)
                hline_left(map, x - 1, y1)
                vline(map, x, y1, y2)
                hline_right(map, x + 1, y2)
            else:
                miny = max(left.y, right.y)
                maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                y = libtcod.random_get_int(None, miny, maxy)

                # catch out-of-bounds attempts
                while y > MAP_HEIGHT - 1:
                         y -= 1

                hline_left(map, right.x - 1, y)
                hline_right(map, right.x, y)

    return True

def make_bsp():
    global map, stairs, bsp_rooms

    baseclasses.objects = [pc.player]

    map = [[baseclasses.Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    #Empty global list for storing room coordinates
    bsp_rooms = []

    #New root node
    bsp = libtcod.bsp_new_with_size(0, 0, MAP_WIDTH, MAP_HEIGHT)

    #Split into nodes
    libtcod.bsp_split_recursive(bsp, 0, DEPTH, MIN_SIZE + 1, MIN_SIZE + 1, 1.5, 1.5)

    #Traverse the nodes and create rooms
    libtcod.bsp_traverse_inverted_level_order(bsp, traverse_node)

    #Random room for the stairs
    stairs_location = random.choice(bsp_rooms)
    bsp_rooms.remove(stairs_location)
    stairs = baseclasses.Object(stairs_location[0], stairs_location[1], '<', 'stairs', libtcod.white, always_visible=True)
    baseclasses.objects.append(stairs)
    stairs.send_to_back()

    #Random room for player start
    player_room = random.choice(bsp_rooms)
    bsp_rooms.remove(player_room)
    pc.player.x = player_room[0]
    pc.player.y = player_room[1]

    #Add monsters and items
    for room in bsp_rooms:
        new_room = baseclasses.Rect(room[0], room[1], 2, 2)
        place_objects(new_room)

    num_to_select = 4                           # set the number to select here.
    list_of_random_items = random.sample(bsp_rooms, num_to_select)

    start_room = list_of_random_items[0]
    monster = bestiary.goblin(start_room[0], start_room[1])
    monster.color = libtcod.red
    monster.ai = ai.WanderingMonster(list_of_random_items, monster.ai)
    monster.ai.owner = monster
    bestiary.upgrade_npc(monster)
    baseclasses.objects.append(monster)

def place_objects(room):
    #this is where we decide the chance of each monster or item appearing.

    #maximum number of monsters per room
    max_monsters = baseclasses.from_dungeon_level([[2, 1], [3, 3], [5, 4]])

    #chance of each monster
    monster_chances = {}
    monster_chances['goblin'] = baseclasses.from_dungeon_level([[60, 1], [30, 2], [15, 3]])
    monster_chances['orc'] = baseclasses.from_dungeon_level([[15, 2], [30, 3], [60, 4]])
    monster_chances['troll'] = baseclasses.from_dungeon_level([[15, 3], [30, 4], [60, 5]])

    #maximum number of items per room
    max_items = baseclasses.from_dungeon_level([[1, 1], [2, 4]])

    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['potion'] = 25  #healing potion always shows up, even if all other items have 0 chance
    item_chances['scroll'] = baseclasses.from_dungeon_level([[25, 2]])
    item_chances['weapon'] = 35
    item_chances['armour'] = 25

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not baseclasses.is_blocked(x, y):
            choice = baseclasses.random_choice(monster_chances)
            if choice == 'orc':
                monster = bestiary.orc(x, y)
            elif choice == 'troll':
                monster = bestiary.troll(x, y)
            elif choice == 'goblin':
                monster = bestiary.goblin(x, y)

            baseclasses.objects.append(monster)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not baseclasses.is_blocked(x, y):
            choice = baseclasses.random_choice(item_chances)
            if choice == 'potion':
                item = equipment.random_potion(x,y)
            elif choice == 'scroll':
                item = equipment.random_scroll(x,y)
            elif choice == 'weapon':
                item = equipment.random_weapon(x,y)
            elif choice == 'armour':
                item = equipment.random_armour(x,y)

            baseclasses.objects.append(item)
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
