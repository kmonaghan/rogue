import tcod

from etc.configuration import CONFIG
from etc.enum import (GameStates, RenderOrder, INVENTORY_STATES)

from menus import character_screen, inventory_menu, level_up_menu, quest_menu, quest_list_menu, game_completed, game_over, game_paused

def get_names_under_mouse(mouse, game_map):
    (x, y) = (mouse.cx, mouse.cy)

    location = ''

    if game_map.current_level.within_bounds(x, y):
            location = str(x) + ',' + str(y)
    else:
        #print("get_names_under_mouse IndexError: " + str(x) + ',' + str(y))
        return ''

    tile_description = ''
    names = ''

    if (game_map.current_level.fov[x, y] or CONFIG.get('debug')):
        tile_description = str(game_map.current_level.tiles[x][y]) + ' '

        names = [str(entity) for entity in game_map.current_level.entities.get_entities_in_position((x, y))]
        names = ', '.join(names)

    return tile_description + location + ' ' + names

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    if (bar_width > total_width):
        bar_width = total_width

    panel.bg[1:total_width, y] = back_color

    if bar_width > 0:
        panel.bg[1:bar_width, y] = bar_color

    panel.print(x + (total_width // 2), y, '{0}: {1}/{2}'.format(name, value, maximum),
                fg=tcod.white, alignment=tcod.CENTER)

def render_menu_console(game_state, screen_width, screen_height, player, quest_request = None):
    if game_state == GameStates.GAME_PAUSED:
        return game_paused(60, screen_width, screen_height)
    elif game_state == GameStates.GAME_OVER:
        return game_over(60, screen_width, screen_height)
    elif game_state == GameStates.GAME_COMPLETE:
        return game_completed(60, screen_width, screen_height)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return character_screen(player, 30, 10, screen_width, screen_height)
    elif game_state in INVENTORY_STATES:
        if game_state == GameStates.INVENTORY_USE:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_EXAMINE:
            inventory_title = 'Press the key next to an item to examine it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_DROP:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
        else:
            inventory_title = 'Esc to cancel.\n'

        return inventory_menu(inventory_title, player, 50, screen_width, screen_height)
    elif game_state == GameStates.QUEST_ONBOARDING:
        return quest_menu('Questing', quest_request, 50, screen_width, screen_height)
    elif game_state == GameStates.QUEST_LIST:
        return quest_list_menu('Press the key next to an quest to get details, or Esc to cancel.\n', player, 50, screen_width, screen_height)
    elif game_state == GameStates.LEVEL_UP:
        return level_up_menu('Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

def render_info_console(info_console, player, game_map):
    info_console.clear()

    info_console.draw_frame(
                0,
                0,
                info_console.width,
                info_console.height,
                "Stats",
                False,
                fg=tcod.white,
                bg=tcod.black,
            )
    render_bar(info_console, 1, 2, info_console.width - 2, 'HP', player.health.hp, player.health.max_hp,
               tcod.light_red, tcod.darker_red)

    render_bar(info_console, 1, 4, info_console.width - 2, 'XP', player.level.current_xp, player.level.experience_to_next_level,
                   tcod.light_green, tcod.darker_green)

    info_console.print(1, 6, 'Dungeon level: {0}'.format(game_map.dungeon_level), tcod.white)

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
