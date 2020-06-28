import tcod

from etc.configuration import CONFIG
from etc.enum import (GameStates, INVENTORY_STATES)

from menus import character_screen, inventory_menu, level_up_menu, quest_menu, quest_list_menu, game_completed, game_over, game_paused

def get_names_under_mouse(x, y, current_level):
    location = ''

    if current_level.within_bounds(x, y):
        location = str(x) + ',' + str(y)

    location_description = location

    if (current_level.explored[x, y] or CONFIG.get('debug')):
        location_description = location_description + ' ' + current_level.tiles[x, y]['name']

    if (current_level.fov[x, y] or CONFIG.get('debug')):
        names = [str(entity) for entity in current_level.entities.get_entities_in_position((x, y))]
        names = ', '.join(names)
        location_description = location_description + ' ' + names

    return location_description

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value / maximum) * total_width)

    if (bar_width > total_width):
        bar_width = total_width

    panel.bg[x:x+total_width, y] = back_color

    if bar_width > 0:
        panel.bg[x:x+bar_width, y] = bar_color

    panel.print(x + (total_width // 2), y, f"{name} {value}/{maximum}",
                fg=tcod.white, alignment=tcod.CENTER)

def render_menu_console(game_state, player, quest_request = None, exclude = []):
    if game_state == GameStates.GAME_PAUSED:
        return game_paused()
    elif game_state == GameStates.GAME_OVER:
        return game_over()
    elif game_state == GameStates.GAME_COMPLETE:
        return game_completed()
    elif game_state == GameStates.CHARACTER_SCREEN:
        return character_screen(player)
    elif game_state in INVENTORY_STATES:
        if game_state == GameStates.INVENTORY_USE:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_EXAMINE:
            inventory_title = 'Press the key next to an item to examine it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_DROP:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_SELECT:
            inventory_title = 'Press the key next to an item to identify it, or Esc to cancel.\n'
        else:
            inventory_title = 'Esc to cancel.\n'

        return inventory_menu(inventory_title, player, exclude)
    elif game_state == GameStates.QUEST_ONBOARDING:
        return quest_menu(quest_request)
    elif game_state == GameStates.QUEST_LIST:
        return quest_list_menu(player)
    elif game_state == GameStates.LEVEL_UP:
        return level_up_menu(player)

def render_info_console(info_console, player, game_map):
    info_console.clear()

    info_console.draw_frame(
                0,
                0,
                info_console.width,
                info_console.height,
                f"Dungeon level: {game_map.dungeon_level}",
                False,
                fg=tcod.white,
                bg=tcod.black,
            )
    bar_width = (info_console.width - 4) // 2

    render_bar(info_console, 1, 2, bar_width, 'HP',
                player.health.hp, player.health.max_hp,
                tcod.light_red, tcod.darker_red)

    render_bar(info_console, info_console.width - bar_width - 1, 2, bar_width, 'XP',
                player.level.current_xp, player.level.experience_to_next_level,
                tcod.light_green, tcod.darker_green)

    return info_console

def render_message_console(message_console, message_log):
    message_console.clear()

    message_console.draw_frame(
                0,
                0,
                message_console.width,
                message_console.height,
                "Messages",
                False,
                fg=tcod.white,
                bg=tcod.black,
            )

    message_log_panel = tcod.console.Console(message_log.width, message_log.height, 'F')

    # Print the game messages, one line at a time
    y = 0
    for message in message_log.messages:
        message_log_panel.print(0, y, message.text, message.color)
        y += 1

    message_log_panel.blit(message_console, 1, 1, 0, 0,
                            message_log_panel.width, message_log_panel.height)

    return message_console
