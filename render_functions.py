import tcod as libtcod

import game_states

from etc.enum import (GameStates, RenderOrder, INVENTORY_STATES)

from menus import character_screen, inventory_menu, level_up_menu, quest_menu, quest_list_menu, game_completed, game_over, game_paused

def get_names_under_mouse(mouse, game_map):
    (x, y) = (mouse.cx, mouse.cy)

    location = ''

    try:
        if game_map.map[x][y]:
            location = str(x) + ',' + str(y)
    except IndexError:
        print("get_names_under_mouse IndexError: " + str(x) + ',' + str(y))
        return ''

    tile_description = ''
    names = ''

    if (game_map.current_level.fov[x, y] or game_states.debug):
        tile_description = game_map.map[x][y].describe() + ' '

        names = [entity.describe() for entity in game_map.entity_map[x][y]]
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
                fg=libtcod.white, alignment=libtcod.CENTER)

def render_menu_console(con, game_state, screen_width, screen_height, player):
    if game_state == GameStates.GAME_PAUSED:
        game_paused(con, 60, screen_width, screen_height)
    elif game_state == GameStates.GAME_OVER:
        game_over(con, 60, screen_width, screen_height)
    elif game_state == GameStates.GAME_COMPLETE:
        game_completed(con, 60, screen_width, screen_height)
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)
    elif game_state in INVENTORY_STATES:
        if game_state == GameStates.INVENTORY_USE:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_EXAMINE:
            inventory_title = 'Press the key next to an item to examine it, or Esc to cancel.\n'
        elif game_state == GameStates.INVENTORY_DROP:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
        else:
            inventory_title = 'Esc to cancel.\n'

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)
    elif game_state == GameStates.QUEST_ONBOARDING:
        quest_menu(con, '', quest_request, 50, screen_width, screen_height)
    elif game_state == GameStates.QUEST_LIST:
        quest_list_menu(con, 'Press the key next to an quest to get details, or Esc to cancel.\n', player, 50, screen_width, screen_height)
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

def render_info_console(info_console, player, game_map):
    info_console.clear()

    info_console.draw_frame(
                0,
                0,
                info_console.width,
                info_console.height,
                "Stats",
                False,
                fg=libtcod.white,
                bg=libtcod.black,
            )
    render_bar(info_console, 1, 2, info_console.width - 2, 'HP', player.health.hp, player.health.max_hp,
               libtcod.light_red, libtcod.darker_red)

    render_bar(info_console, 1, 4, info_console.width - 2, 'XP', player.level.current_xp, player.level.experience_to_next_level,
                   libtcod.light_green, libtcod.darker_green)

    info_console.print(1, 6, 'Dungeon level: {0}'.format(game_map.dungeon_level), libtcod.white)

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
                fg=libtcod.white,
                bg=libtcod.black,
            )
    # Print the game messages, one line at a time
    y = 2
    for message in message_log.messages:
        message_console.print(1, y, message.text, message.color)
        y += 1

    return message_console

def draw_entity(con, entity, fov_map, game_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.map[entity.x][entity.y].explored) or entity.always_visible or game_states.debug:
        libtcod.console_set_default_foreground(con, entity.display_color())
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)

def clear_entity(con, entity, game_map):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
