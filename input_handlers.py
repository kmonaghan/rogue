import tcod as libtcod

from etc.enum import GameStates, InputTypes, LevelUp, INVENTORY_STATES

def handle_keys(key, game_state):
    if game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)
    elif game_state == GameStates.GAME_COMPLETE:
        return handle_game_complete_keys(key)
    elif game_state == GameStates.GAME_START:
        return handle_main_menu(key)
    elif game_state == GameStates.GAME_OVER:
        return handle_game_over_keys(key)
    elif game_state == GameStates.GAME_PAUSED:
        return handle_game_paused_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in INVENTORY_STATES:
        return handle_inventory_keys(key)
    elif game_state == GameStates.QUEST_LIST:
        return handle_show_quests(key)
    elif game_state == GameStates.QUEST_ONBOARDING:
        return handle_quests_onboarding(key)

    return {}


def handle_player_turn_keys(key):
    #print(key)
    key_char = chr(key.c)

    # Movement keys
    if key.vk == libtcod.KEY_UP or key_char == 'k':
        return {InputTypes.MOVE: (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j':
        return {InputTypes.MOVE: (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h':
        return {InputTypes.MOVE: (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l':
        return {InputTypes.MOVE: (1, 0)}
    elif key_char == 'y':
        return {InputTypes.MOVE: (-1, -1)}
    elif key_char == 'u':
        return {InputTypes.MOVE: (1, -1)}
    elif key_char == 'b':
        return {InputTypes.MOVE: (-1, 1)}
    elif key_char == 'n':
        return {InputTypes.MOVE: (1, 1)}
    elif key_char == 'z':
        return {InputTypes.WAIT: True}
    elif key_char == ']':
        return {InputTypes.DEBUG_ON: True}
    elif key_char == '[':
        return {InputTypes.DEBUG_OFF: False}

    if key_char == 'g':
        return {InputTypes.PICKUP: True}

    elif key_char == 'i':
        return {InputTypes.INVENTORY_USE: True}

    elif key_char == 'd':
        return {InputTypes.INVENTORY_DROP: True}

    elif key_char == 'e':
        return {InputTypes.INVENTORY_EXAMINE: True}

    elif key_char == 'q':
        return {InputTypes.QUEST_LIST: True}

    elif key.vk == key_char == ',' or key_char == '.':
        return {InputTypes.TAKE_STAIRS: True}

    elif key_char == 'c':
        return {InputTypes.CHARACTER_SCREEN: True}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {InputTypes.FULLSCREEN: True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {InputTypes.EXIT: True}

    # No key was pressed
    return {}


def handle_targeting_keys(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}

def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {InputTypes.INVENTORY_INDEX: index}

    if key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {InputTypes.EXIT: True}

    return {}

def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {InputTypes.GAME_NEW: True}
    elif key_char == 'b':
        return {InputTypes.GAME_LOAD: True}
    elif key_char == 'c' or key.vk == libtcod.KEY_ESCAPE:
        return {InputTypes.GAME_EXIT: True}

    return {}


def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'a':
            return {InputTypes.LEVEL_UP: LevelUp.HEALTH}
        elif key_char == 'b':
            return {InputTypes.LEVEL_UP: LevelUp.STRENGTH}
        elif key_char == 'c':
            return {InputTypes.LEVEL_UP: LevelUp.DEFENCE}

    return {}

def handle_show_quests(key):
    index = key.c - ord('a')

    if index >= 0:
        return {InputTypes.QUEST_INDEX: index}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {InputTypes.FULLSCREEN: True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {InputTypes.EXIT: True}

    return {}

def handle_quests_onboarding(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'a':
            return {InputTypes.QUEST_RESPONSE: True}
        elif key_char == 'b':
            return {InputTypes.QUEST_RESPONSE: False}
        elif key.vk == libtcod.KEY_ESCAPE:
            # Exit the menu
            return {InputTypes.EXIT: True}

    return {}

def handle_character_screen(key):
    return {InputTypes.EXIT: True}

def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {InputTypes.CLICK_LEFT: (x, y)}
    elif mouse.rbutton_pressed:
        return {InputTypes.CLICK_RIGHT: (x, y)}

    return {}

def handle_game_complete_keys(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {InputTypes.GAME_RESTART: True}
    elif key_char == 'b' or key.vk == libtcod.KEY_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}

def handle_game_over_keys(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {InputTypes.GAME_RESTART: True}
    elif key_char == 'b':
        return {InputTypes.CHARACTER_SCREEN: True}
    elif key_char == 'c':
        return {InputTypes.INVENTORY_EXAMINE: True}
    elif key_char == 'd':
        return {InputTypes.QUEST_LIST: True}
    elif key_char == 'e' or key.vk == libtcod.KEY_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}

def handle_game_paused_keys(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {InputTypes.GAME_RESTART: True}
    elif key_char == 'b':
        return {InputTypes.GAME_SAVE: True}
    elif key_char == 'c':
        return {InputTypes.GAME_EXIT: True}
    elif key.vk == libtcod.KEY_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}
