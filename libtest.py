import libtcodpy as libtcod
import math
import shelve

import equipment
import characterclass
import messageconsole
import pc
import baseclasses
import gamemap

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
#MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
#MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 10

LIMIT_FPS = 20  #20 frames-per-second maximum

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
    global mouse
    #return a string with the names of all objects under the mouse

    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in baseclasses.objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(baseclasses.fov_map, obj.x, obj.y)]

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def render_all():
    global color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(baseclasses.fov_map, pc.player.x, pc.player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #go through all tiles, and set their background color according to the FOV
        for y in range(gamemap.MAP_HEIGHT):
            for x in range(gamemap.MAP_WIDTH):
                visible = libtcod.map_is_in_fov(baseclasses.fov_map, x, y)
                wall = gamemap.map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if gamemap.map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(baseclasses.con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(baseclasses.con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(baseclasses.con, x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(baseclasses.con, x, y, color_light_ground, libtcod.BKGND_SET )
                        #since it's visible, explore it
                    gamemap.map[x][y].explored = True

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in baseclasses.objects:
        if object != pc.player:
            object.draw()
    pc.player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(baseclasses.con, 0, 0, gamemap.MAP_WIDTH, gamemap.MAP_HEIGHT, 0, 0, 0)


    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in messageconsole.game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT,line)
        y += 1

    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', pc.player.fighter.hp, pc.player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(gamemap.dungeon_level))

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def player_move_or_attack(dx, dy):
    global fov_recompute

    #the coordinates the player is moving to/attacking
    x = pc.player.x + dx
    y = pc.player.y + dy

    #try to find an attackable object there
    target = None
    for object in baseclasses.objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    #attack if target found, move otherwise
    if target is not None:
        pc.player.fighter.attack(target)
    else:
        pc.player.move(dx, dy)
        fov_recompute = True


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(baseclasses.con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen)

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(equipment.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in equipment.inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(equipment.inventory) == 0: return None
    return equipment.inventory[index].item

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

def handle_keys():
    global key

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if baseclasses.game_state == 'playing':
        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif key.vk == libtcod.KEY_KP5:
            pass  #do nothing ie wait for the monster to come to you
        else:
            #test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick up an item
                for object in baseclasses.objects:  #look for an item in the player's tile
                    if object.x == pc.player.x and object.y == pc.player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == 'c':
                #show character information
                level_up_xp = LEVEL_UP_BASE + pc.player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(pc.player.level) + '\nExperience: ' + str(pc.player.fighter.xp) +
                       '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(pc.player.fighter.max_hp) +
                       '\nAttack: ' + str(pc.player.fighter.power) + '\nDefense: ' + str(pc.player.fighter.defense), CHARACTER_SCREEN_WIDTH)

            if (key_char == '<') or (key_char == ','):
                #go down stairs, if the player is on them
                if gamemap.stairs.x == pc.player.x and gamemap.stairs.y == pc.player.y:
                    next_level()

            #print "Pressed: " + key_char
            return 'didnt-take-turn'

def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = LEVEL_UP_BASE + pc.player.level * LEVEL_UP_FACTOR
    if pc.player.fighter.xp >= level_up_xp:
        #it is! level up and ask to raise some stats
        pc.player.level += 1
        pc.player.fighter.xp -= level_up_xp
        messageconsole.message('Your battle skills grow stronger! You reached level ' + str(pc.player.level) + '!', libtcod.yellow)

        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(pc.player.fighter.max_hp) + ')',
                           'Strength (+1 attack, from ' + str(pc.player.fighter.power) + ')',
                           'Agility (+1 defense, from ' + str(pc.player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)

        if choice == 0:
            pc.player.fighter.base_max_hp += 20
            pc.player.fighter.hp += 20
        elif choice == 1:
            pc.player.fighter.base_power += 1
        elif choice == 2:
            pc.player.fighter.base_defense += 1

def target_tile(max_range=None):
    global key, mouse
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx, mouse.cy)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(baseclasses.fov_map, x, y) and
                (max_range is None or pc.player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in baseclasses.objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != pc.player:
                return obj

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in baseclasses.objects:
        if object.fighter and not object == pc.player and libtcod.map_is_in_fov(baseclasses.fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = pc.player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = gamemap.map
    file['objects'] = baseclasses.objects
    file['player_index'] = baseclasses.objects.index(pc.player)  #index of player in objects list
    file['stairs_index'] = baseclasses.objects.index(gamemap.stairs)  #same for the stairs
    file['inventory'] = equipment.inventory
    file['game_msgs'] = messageconsole.game_msgs
    file['game_state'] = baseclasses.game_state
    file['dungeon_level'] = gamemap.dungeon_level
    file.close()

def load_game():
    file = shelve.open('savegame', 'r')
    gamemap.map = file['map']
    baseclasses.objects = file['objects']
    pc.player = baseclasses.objects[file['player_index']]  #get index of player in objects list and access it
    gamemap.stairs = baseclasses.objects[file['stairs_index']]  #same for the stairs
    equipment.inventory = file['inventory']
    messageconsole.game_msgs = file['game_msgs']
    baseclasses.game_state = file['game_state']
    gamemap.dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()

def new_game():
    pc.create_player()

    #generate map (at this point it's not drawn to the screen)
    gamemap.dungeon_level = 1
    #gamemap.make_map()
    gamemap.make_bsp()
    initialize_fov()

    baseclasses.game_state = 'playing'

    #a warm welcoming message!
    messageconsole.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

def next_level():
    #advance to the next level
    messageconsole.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    pc.player.fighter.heal(pc.player.fighter.max_hp / 2)  #heal the player by 50%

    gamemap.dungeon_level += 1
    messageconsole.message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    #gamemap.make_map()
    gamemap.make_bsp()

    initialize_fov()

def initialize_fov():
    global fov_recompute
    fov_recompute = True

    #create the FOV map, according to the generated map
    baseclasses.fov_map = libtcod.map_new(gamemap.MAP_WIDTH, gamemap.MAP_HEIGHT)
    for y in range(gamemap.MAP_HEIGHT):
        for x in range(gamemap.MAP_WIDTH):
            libtcod.map_set_properties(baseclasses.fov_map, x, y, not gamemap.map[x][y].block_sight, not gamemap.map[x][y].blocked)

    libtcod.console_clear(baseclasses.con)  #unexplored areas start black (which is the default background color)

def play_game():
    global key, mouse

    player_action = None

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    #main loop
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        #render the screen
        render_all()

        libtcod.console_flush()

        #level up if needed
        check_level_up()

        #erase all objects at their old locations, before they move
        for object in baseclasses.objects:
            object.clear()

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        #let monsters take their turn
        if baseclasses.game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in baseclasses.objects:
                if object.ai:
                    object.ai.take_turn()

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Jotaf')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:  #quit
            break

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
baseclasses.con = libtcod.console_new(gamemap.MAP_WIDTH, gamemap.MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu()
