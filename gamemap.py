import libtcodpy as libtcod
import pc
import baseclasses
import equipment
import characterclass
import messageconsole
import random
import beastery

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43

#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

DEPTH = 10
MIN_SIZE = 5
#set this to tru to have a full map
FULL_ROOMS = False

#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8

FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25


dungeon_level = 1

map = []
stairs = None

def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map, stairs

    #the list of objects with just the player
    baseclasses.objects = [pc.player]

    #fill map with "blocked" tiles
    map = [[ baseclasses.Tile(True)
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        new_room = baseclasses.Rect(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                pc.player.x = new_x
                pc.player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #add some contents to this room, such as monsters
            place_objects(new_room)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #create stairs at the center of the last room
    stairs = baseclasses.Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
    baseclasses.objects.append(stairs)
    stairs.send_to_back()  #so it's drawn below the monsters

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

def place_objects(room):
    #this is where we decide the chance of each monster or item appearing.

    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 3], [5, 4]])

    #chance of each monster
    monster_chances = {}
    monster_chances['goblin'] = from_dungeon_level([[60, 1], [30, 2], [15, 3]])
    monster_chances['orc'] = from_dungeon_level([[15, 2], [30, 3], [60, 4]])
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 4], [60, 5]])

    #maximum number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])

    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 2]])
    item_chances['fireball'] =  from_dungeon_level([[25, 3]])
    item_chances['confuse'] =   from_dungeon_level([[10, 4]])
    item_chances['sword'] =     from_dungeon_level([[5, 2]])
    item_chances['shield'] =    from_dungeon_level([[15, 2]])
    item_chances['helmet'] =    from_dungeon_level([[15, 2]])

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not baseclasses.is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'orc':
                monster = beastery.orc(x, y)
            elif choice == 'troll':
                monster = beastery.troll(x, y)
            elif choice == 'goblin':
                monster = beastery.goblin(x, y)

            baseclasses.objects.append(monster)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not baseclasses.is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = equipment.Item(use_function=cast_heal)
                item = baseclasses.Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)

            elif choice == 'lightning':
                #create a lightning bolt scroll
                item_component = equipment.Item(use_function=cast_lightning)
                item = baseclasses.Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

            elif choice == 'fireball':
                #create a fireball scroll
                item_component = equipment.Item(use_function=cast_fireball)
                item = baseclasses.Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

            elif choice == 'confuse':
                #create a confuse scroll
                item_component = equipment.Item(use_function=cast_confuse)
                item = baseclasses.Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

            elif choice == 'sword':
                #create a sword
                equipment_component = equipment.Equipment(slot='right hand', power_bonus=3)
                item = baseclasses.Object(x, y, '/', 'sword', libtcod.sky, gear=equipment_component)

            elif choice == 'shield':
                #create a shield
                equipment_component = equipment.Equipment(slot='left hand', defense_bonus=1)
                item = baseclasses.Object(x, y, '[', 'shield', libtcod.darker_orange, gear=equipment_component)

            elif choice == 'helmet':
                #create a helmet
                equipment_component = equipment.Equipment(slot='head', defense_bonus=1)
                item = baseclasses.Object(x, y, '^', 'helmet', libtcod.darker_orange, gear=equipment_component)

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

def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def cast_heal():
    #heal the player
    if pc.player.fighter.hp == pc.player.fighter.max_hp:
        messageconsole.message('You are already at full health.', libtcod.red)
        return 'cancelled'

    messageconsole.message('Your wounds start to feel better!', libtcod.light_violet)
    pc.player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  #no enemy found within maximum range
        messageconsole.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    #zap it!
    messageconsole.message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    messageconsole.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    messageconsole.message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

    for obj in baseclasses.objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            messageconsole.message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)

def cast_confuse():
    #ask the player for a target to confuse
    messageconsole.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    messageconsole.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)
