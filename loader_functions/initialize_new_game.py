import libtcodpy as libtcod

from bestiary import create_player

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder


def get_constants():
    window_title = 'Roguelike Tutorial Revised'

    screen_width = 71
    screen_height = 51

    bar_width = 20
    panel_height = 10
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = screen_width
    map_height = screen_height - panel_height - 1

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': libtcod.darkest_sepia,
        'dark_ground': libtcod.darker_sepia,
        'light_wall': libtcod.dark_sepia,
        'light_ground': libtcod.sepia
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colors': colors
    }

    return constants


def get_game_variables(constants):
    player = create_player()

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    map_height = constants['map_height']
    map_width = constants['map_width']

    game_map = GameMap()

    game_map.create_floor(player, message_log, constants)

    game_state = GameStates.PLAYERS_TURN

    return player, game_map, message_log, game_state
