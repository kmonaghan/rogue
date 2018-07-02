import libtcodpy as libtcod

from bestiary import create_player

from entity import Entity

from equipment_slots import EquipmentSlots

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder


def get_constants():
    window_title = 'Roguelike Tutorial Revised'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 10
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 40

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
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
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
    entities = [player]

#    if (game_state.dungeon_level <= 2):
#        map_height = (constants['map_height'] / 3) * 2
#        map_width = (constants['map_width'] / 3) * 2
#    else:
#        map_height = constants['map_height']
#        map_width = constants['map_width']

    map_height = constants['map_height']
    map_width = constants['map_width']

    game_map = GameMap(map_width, map_height)
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      map_width, map_height, player)

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state
