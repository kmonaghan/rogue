import libtcodpy as libtcod
import math
import shelve

import bestiary
import equipment
import messageconsole
import baseclasses
import gamemap
import screenrendering
import characterclass

import game_state

from equipment_slots import EquipmentSlots

LIMIT_FPS = 20  #20 frames-per-second maximum
CHARACTER_SCREEN_WIDTH = 30

def player_move_or_attack(dx, dy):
    #the coordinates the player is moving to/attacking
    x = game_state.player.x + dx
    y = game_state.player.y + dy

    #try to find an attackable object there
    target = None
    for object in game_state.objects:
        if (object.fighter and object.x == x and object.y == y) or (object.questgiver and object.x == x and object.y == y):
            target = object
            break

    #attack if target found, move otherwise
    if target is not None:
        if (target.fighter is not None):
            game_state.player.fighter.attack(target)
        elif (target.questgiver is not None):
            target.questgiver.talk(game_state.player)
    else:
        game_state.player.move(dx, dy)
        screenrendering.fov_recompute = True

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(game_state.player.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in game_state.player.inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                if (item.equipment.slot == EquipmentSlots.MAIN_HAND):
                    text = text + ' (held in right hand)'
                elif (item.equipment.slot == EquipmentSlots.OFF_HAND):
                    text = text + ' (held in left hand)'
                elif (item.equipment.slot == EquipmentSlots.HEAD):
                    text = text + ' (worn on head)'
                elif (item.equipment.slot == EquipmentSlots.CHEST):
                    text = text + ' (worn on chest)'
            options.append([text, item.color])

    index = screenrendering.menu(header, options, screenrendering.INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(game_state.player.inventory) == 0: return None
    return game_state.player.inventory[index].item

def msgbox(text, width=50):
    screenrendering.menu(text, [], width)  #use menu() as a sort of "message box"

def handle_keys():
    if screenrendering.key.vk == libtcod.KEY_ENTER and screenrendering.key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif screenrendering.key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if baseclasses.game_status == 'playing':
        #movement keys
        if screenrendering.key.vk == libtcod.KEY_UP or screenrendering.key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif screenrendering.key.vk == libtcod.KEY_DOWN or screenrendering.key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif screenrendering.key.vk == libtcod.KEY_LEFT or screenrendering.key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif screenrendering.key.vk == libtcod.KEY_RIGHT or screenrendering.key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif screenrendering.key.vk == libtcod.KEY_HOME or screenrendering.key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif screenrendering.key.vk == libtcod.KEY_PAGEUP or screenrendering.key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif screenrendering.key.vk == libtcod.KEY_END or screenrendering.key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif screenrendering.key.vk == libtcod.KEY_PAGEDOWN or screenrendering.key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif screenrendering.key.vk == libtcod.KEY_KP5:
            pass  #do nothing ie wait for the npc to come to you
        else:
            #test for other keys
            key_char = chr(screenrendering.key.c)

            if key_char == 'g':
                #pick up an item
                for object in game_state.objects:  #look for an item in the player's tile
                    if object.x == game_state.player.x and object.y == game_state.player.y and object.item:
                        object.item.pick_up(game_state.player)
                        break

            if key_char == 'c':
                #show character information
                level_up_xp = game_state.player.experience_to_next_level
                msgbox('Character Information\n\nLevel: ' + str(game_state.player.level) + '\nExperience: ' + str(game_state.player.level.current_xp) +
                       '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(game_state.player.fighter.max_hp) +
                       '\nAttack: ' + str(game_state.player.fighter.power) + '\nDefense: ' + str(game_state.player.fighter.defense), CHARACTER_SCREEN_WIDTH)

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == 'e':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to examine it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.examine()

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'q':
                game_state.player.list_quests()

            if key_char == ']':
                game_state.debug = True

            if key_char == '[':
                game_state.debug = False

            if (key_char == '<') or (key_char == ','):
                #go down stairs, if the player is on them
                if gamemap.stairs.x == game_state.player.x and gamemap.stairs.y == game_state.player.y:
                    next_level()

            #print "Pressed: " + key_char
            return 'didnt-take-turn'

def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = game_state.map
    file['objects'] = game_state.objects
    file['player_index'] = game_state.objects.index(game_state.player)  #index of player in objects list
    file['game_msgs'] = messageconsole.game_msgs
    file['game_status'] = baseclasses.game_status
    file['dungeon_level'] = gamemap.dungeon_level
    if (gamemap.stairs != None):
        file['stairs_index'] = game_state.objects.index(gamemap.stairs)  #same for the stairs
    file.close()

def load_game():
    file = shelve.open('savegame', 'r')
    game_state.map = file['map']
    game_state.objects = file['objects']
    game_state.player = game_state.objects[file['player_index']]  #get index of player in objects list and access it
    gamemap.stairs = game_state.objects[file['stairs_index']]  #same for the stairs
    messageconsole.game_msgs = file['game_msgs']
    baseclasses.game_status = file['game_status']
    game_state.dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()

def new_game():
    game_state.player = bestiary.create_player()

    #generate map (at this point it's not drawn to the screen)
    game_state.dungeon_level = 1
    gamemap.make_bsp()
    screenrendering.initialize_fov()

    baseclasses.game_status = 'playing'

    #a warm welcoming message!
    messageconsole.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

def next_level():
    #advance to the next level
    total = 0
    for y in range(gamemap.MAP_HEIGHT):
        for x in range(gamemap.MAP_WIDTH):
            if (game_state.map[x][y].isFloor() and game_state.map[x][y].explored):
                total += 1

    xp = total / 10

    game_state.player.level.add_xp(xp)

    messageconsole.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    game_state.player.fighter.heal(game_state.player.fighter.max_hp / 2)  #heal the player by 50%

    game_state.dungeon_level += 1
    messageconsole.message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)

    gamemap.make_bsp()

    screenrendering.initialize_fov()

def play_game():
    player_action = None

    screenrendering.mouse = libtcod.Mouse()
    screenrendering.key = libtcod.Key()
    #main loop
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, screenrendering.key, screenrendering.mouse)
        #render the screen
        screenrendering.render_all()

        libtcod.console_flush()

        #erase all objects at their old locations, before they move
        for object in game_state.objects:
            object.clear()

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        #let npcs take their turn
        if baseclasses.game_status == 'playing' and player_action != 'didnt-take-turn':
            for object in game_state.objects:
                if object.ai:
                    object.ai.take_turn()

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, screenrendering.SCREEN_WIDTH/2, screenrendering.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        libtcod.console_print_ex(0, screenrendering.SCREEN_WIDTH/2, screenrendering.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Jotaf')

        #show options and wait for the player's choice
        choice = screenrendering.menu('', [['Play a new game',libtcod.white], ['Continue last game',libtcod.white], ['Quit',libtcod.white]], 24)

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
libtcod.console_init_root(screenrendering.SCREEN_WIDTH, screenrendering.SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
baseclasses.con = libtcod.console_new(gamemap.MAX_MAP_WIDTH, gamemap.MAX_MAP_HEIGHT)
screenrendering.panel = libtcod.console_new(screenrendering.SCREEN_WIDTH, screenrendering.PANEL_HEIGHT)

main_menu()
