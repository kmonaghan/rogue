import libtcodpy as libtcod

from enum import Enum

import game_states
from render_order import RenderOrder

from menus import character_screen, inventory_menu, level_up_menu, quest_menu, quest_list_menu, game_completed

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.describe() for entity in entities
             if entity.x == x and entity.y == y and (libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or game_states.debug)]
    names = ', '.join(names)

    return str(x) + ',' + str(y) + ' ' + names


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    if (bar_width > total_width):
        bar_width = total_width

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors, game_state, quest_request = None):
    if fov_recompute:
    # Draw all the tiles in the game map
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)

                if game_states.debug:
                    libtcod.console_set_char_background(con, x, y, game_map.map[x][y].fov_color, libtcod.BKGND_SET)
                    if visible:
                        game_map.map[x][y].explored = True
                else:
                    if visible:
                        libtcod.console_set_char_background(con, x, y, game_map.map[x][y].fov_color, libtcod.BKGND_SET)

                        game_map.map[x][y].explored = True
                    elif game_map.map[x][y].explored:
                        libtcod.console_set_char_background(con, x, y, game_map.map[x][y].out_of_fov_color, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, libtcod.black, libtcod.BKGND_SET)

    entities_in_render_order = sorted(game_map.entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    render_bar(panel, 1, 3, bar_width, 'XP', player.level.current_xp, player.level.experience_to_next_level,
                   libtcod.light_green, libtcod.darker_green)

    libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon level: {0}'.format(game_map.dungeon_level))

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, game_map.entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state == game_states.GameStates.GAME_COMPLETE:
        game_completed(con, 60, screen_width, screen_height)

    elif game_state in (game_states.GameStates.SHOW_INVENTORY, game_states.GameStates.DROP_INVENTORY, game_states.GameStates.EXAMINE_INVENTORY):
        if game_state == game_states.GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        elif game_state == game_states.GameStates.EXAMINE_INVENTORY:
            inventory_title = 'Press the key next to an item to examine it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    elif game_state == game_states.GameStates.QUEST_ONBOARDING:
        quest_menu(con, '', quest_request, 50, screen_width, screen_height)

    elif game_state == game_states.GameStates.SHOW_QUESTS:
        quest_list_menu(con, 'Press the key next to an quest to get details, or Esc to cancel.\n', player, 50, screen_width, screen_height)

    elif game_state == game_states.GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    elif game_state == game_states.GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

def clear_all(con, game_map):
    for entity in game_map.entities:
        clear_entity(con, entity, game_map)

def draw_entity(con, entity, fov_map, game_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.map[entity.x][entity.y].explored) or entity.always_visible or game_states.debug:
        libtcod.console_set_default_foreground(con, entity.display_color())
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)

def clear_entity(con, entity, game_map):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
