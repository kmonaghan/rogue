import libtcodpy as libtcod
import gamemap
import baseclasses
import messageconsole
import characterclass

import game_state

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
#MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
#MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 10

key = None
mouse = None
fov_recompute = None
panel = None

#color_dark_wall = libtcod.Color(0, 0, 100)
#color_light_wall = libtcod.Color(130, 110, 50)
#color_dark_ground = libtcod.Color(50, 50, 150)
#color_light_ground = libtcod.Color(200, 180, 50)

color_dark_wall = libtcod.darkest_sepia
color_light_wall = libtcod.dark_sepia
color_dark_ground = libtcod.darker_sepia
color_light_ground = libtcod.sepia


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
    for (option_text, option_color) in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_set_default_foreground(window, option_color)
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

def get_names_under_mouse():
    #return a string with the names of all objects under the mouse

    (x, y) = (mouse.cx, mouse.cy)

    x_offset = (gamemap.MAX_MAP_WIDTH - gamemap.MAP_WIDTH)/ 2
    y_offset = (gamemap.MAX_MAP_HEIGHT - gamemap.MAP_HEIGHT) / 2

    x -= x_offset
    y -= y_offset

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in game_state.objects
             if obj.x == x and obj.y == y and (libtcod.map_is_in_fov(baseclasses.fov_map, obj.x, obj.y) or game_state.debug)]

    names = ', '.join(names)  #join the names, separated by commas
    return str(x) + ',' + str(y) + ' ' + names.capitalize()

def initialize_fov():
    global fov_recompute
    fov_recompute = True

    #create the FOV map, according to the generated map
    baseclasses.fov_map = libtcod.map_new(gamemap.MAP_WIDTH, gamemap.MAP_HEIGHT)
    for y in range(gamemap.MAP_HEIGHT):
        for x in range(gamemap.MAP_WIDTH):
            libtcod.map_set_properties(baseclasses.fov_map, x, y, not game_state.map[x][y].block_sight, not game_state.map[x][y].blocked)

    libtcod.console_clear(baseclasses.con)  #unexplored areas start black (which is the default background color)

def render_all():
    global color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(baseclasses.fov_map, game_state.player.x, game_state.player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        x_offset = (gamemap.MAX_MAP_WIDTH - gamemap.MAP_WIDTH)/ 2
        y_offset = (gamemap.MAX_MAP_HEIGHT - gamemap.MAP_HEIGHT) / 2

        #go through all tiles, and set their background color according to the FOV
        for y in range(gamemap.MAP_HEIGHT):
            for x in range(gamemap.MAP_WIDTH):
                visible = (libtcod.map_is_in_fov(baseclasses.fov_map, x, y) or game_state.debug)
                wall = game_state.map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if game_state.map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(baseclasses.con, x + x_offset, y + y_offset, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(baseclasses.con, x + x_offset, y + y_offset, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(baseclasses.con, x + x_offset, y + y_offset, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(baseclasses.con, x + x_offset, y + y_offset, color_light_ground, libtcod.BKGND_SET )
                        #since it's visible, explore it
                    game_state.map[x][y].explored = True

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in game_state.objects:
        if object != game_state.player:
            object.draw()
    game_state.player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(baseclasses.con, 0, 0, gamemap.MAX_MAP_WIDTH, gamemap.MAX_MAP_HEIGHT, 0, 0, 0)

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
    render_bar(1, 1, BAR_WIDTH, 'HP', game_state.player.fighter.hp, game_state.player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    level_up_xp = characterclass.LEVEL_UP_BASE + game_state.player.level * characterclass.LEVEL_UP_FACTOR
    render_bar(1, 3, BAR_WIDTH, 'XP', game_state.player.fighter.xp, level_up_xp,
               libtcod.light_green, libtcod.darker_green)

    libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(gamemap.dungeon_level))

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

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
