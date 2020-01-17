import tcod

from etc.configuration import CONFIG
from etc.enum import GameStates, InputTypes, LevelUp, INVENTORY_STATES

def handle_keys(event, game_state):
    if game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(event)
    elif game_state == GameStates.GAME_COMPLETE:
        return handle_game_complete_keys(event)
    elif game_state == GameStates.GAME_START:
        return handle_main_menu(event)
    elif game_state == GameStates.GAME_OVER:
        return handle_game_over_keys(event)
    elif game_state == GameStates.GAME_PAUSED:
        return handle_game_paused_keys(event)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(event)
    elif game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(event)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(event)
    elif game_state in INVENTORY_STATES:
        return handle_inventory_keys(event)
    elif game_state == GameStates.QUEST_LIST:
        return handle_show_quests(event)
    elif game_state == GameStates.QUEST_ONBOARDING:
        return handle_quests_onboarding(event)

    return {}


def handle_player_turn_keys(event):
    # Movement keys
    if event.sym == tcod.event.K_UP or event.sym == ord('k'):
        return {InputTypes.MOVE: (0, -1)}
    elif event.sym == tcod.event.K_DOWN or event.sym == ord('j'):
        return {InputTypes.MOVE: (0, 1)}
    elif event.sym == tcod.event.K_LEFT or event.sym == ord('h'):
        return {InputTypes.MOVE: (-1, 0)}
    elif event.sym == tcod.event.K_RIGHT or event.sym == ord('l'):
        return {InputTypes.MOVE: (1, 0)}
    elif event.sym == ord('y'):
        return {InputTypes.MOVE: (-1, -1)}
    elif event.sym == ord('u'):
        return {InputTypes.MOVE: (1, -1)}
    elif event.sym == ord('b'):
        return {InputTypes.MOVE: (-1, 1)}
    elif event.sym == ord('n'):
        return {InputTypes.MOVE: (1, 1)}
    elif event.sym == ord('z'):
        return {InputTypes.WAIT: True}
    elif event.sym == ord(']'):
        return {InputTypes.DEBUG_ON: True}
    elif event.sym == ord('['):
        return {InputTypes.DEBUG_OFF: False}

    if event.sym == ord('g'):
        return {InputTypes.PICKUP: True}

    elif event.sym == ord('i'):
        return {InputTypes.INVENTORY_USE: True}

    elif event.sym == ord('d'):
        return {InputTypes.INVENTORY_DROP: True}

    elif event.sym == ord('e'):
        return {InputTypes.INVENTORY_EXAMINE: True}

    elif event.sym == ord('q'):
        return {InputTypes.QUEST_LIST: True}

    elif event.sym == ord(',') or event.sym == ord('.'):
        return {InputTypes.TAKE_STAIRS: True}

    elif event.sym == ord('c'):
        return {InputTypes.CHARACTER_SCREEN: True}

    elif event.sym == tcod.event.K_ESCAPE:
        # Exit the game
        return {InputTypes.EXIT: True}

    if CONFIG.get('debug') and event.sym == ord('r'):
        return {InputTypes.RELOAD_LEVEL: True}

    if CONFIG.get('debug') and event.sym == ord('o'):
        return {InputTypes.SHOW_DIJKSTRA_PLAYER: True}

    if CONFIG.get('debug') and event.sym == ord('p'):
        return {InputTypes.SHOW_DIJKSTRA_FLEE: True}

    if CONFIG.get('debug') and event.sym == ord('x'):
        return {InputTypes.DOWN_LEVEL: True}

    # No key was pressed
    return {}


def handle_targeting_keys(event):
    if event.sym == tcod.event.K_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}

def handle_inventory_keys(event):
    index = event.sym - ord('a')

    if index >= 0:
        return {InputTypes.INVENTORY_INDEX: index}

    if event.sym == tcod.event.K_ESCAPE:
        # Exit the menu
        return {InputTypes.EXIT: True}

    return {}

def handle_main_menu(event):
    if event.sym == ord('a'):
        return {InputTypes.GAME_NEW: True}
    elif event.sym == ord('b'):
        return {InputTypes.GAME_LOAD: True}
    elif event.sym == ord('c') or event.sym == tcod.event.K_ESCAPE:
        return {InputTypes.GAME_EXIT: True}

    return {}


def handle_level_up_menu(event):
    if event.sym == ord('a'):
        return {InputTypes.LEVEL_UP: LevelUp.HEALTH}
    elif event.sym == ord('b'):
        return {InputTypes.LEVEL_UP: LevelUp.STRENGTH}
    elif event.sym == ord('c'):
        return {InputTypes.LEVEL_UP: LevelUp.DEFENCE}

    return {}

def handle_show_quests(event):
    index = event.sym - ord('a')

    if index >= 0:
        return {InputTypes.QUEST_INDEX: index}

    if event.sym == tcod.event.K_ESCAPE:
        # Exit the menu
        return {InputTypes.EXIT: True}

    return {}

def handle_quests_onboarding(event):
    if event.sym == ord('a'):
        return {InputTypes.QUEST_RESPONSE: True}
    elif event.sym == ord('b'):
        return {InputTypes.QUEST_RESPONSE: False}
    elif event.sym == tcod.event.K_ESCAPE:
        # Exit the menu
        return {InputTypes.EXIT: True}

    return {}

def handle_character_screen(event):
    return {InputTypes.EXIT: True}

def handle_game_complete_keys(event):
    if event.sym == ord('a'):
        return {InputTypes.GAME_RESET: True}
    elif event.sym == ord('b'):
        return {InputTypes.GAME_RESTART: True}
    elif event.sym == ord('c') or event.sym == tcod.event.K_ESCAPE:
        return {InputTypes.GAME_EXIT: True}

    return {}

def handle_game_over_keys(event):
    if event.sym == ord('a'):
        return {InputTypes.GAME_RESTART: True}
    elif event.sym == ord('b'):
        return {InputTypes.CHARACTER_SCREEN: True}
    elif event.sym == ord('c'):
        return {InputTypes.INVENTORY_EXAMINE: True}
    elif event.sym == ord('d'):
        return {InputTypes.QUEST_LIST: True}
    elif event.sym == ord('e') or event.sym == tcod.event.K_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}

def handle_game_paused_keys(event):
    if event.sym == ord('a'):
        return {InputTypes.GAME_RESTART: True}
    elif event.sym == ord('b'):
        return {InputTypes.GAME_SAVE: True}
    elif event.sym == ord('c'):
        return {InputTypes.GAME_EXIT: True}
    elif event.sym == tcod.event.K_ESCAPE:
        return {InputTypes.EXIT: True}

    return {}
