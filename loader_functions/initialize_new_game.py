import tcod as libtcod

from bestiary import create_player

from game_messages import MessageLog

from map_objects.game_map import GameMap

from render_functions import RenderOrder

import pubsub

import quest

from etc.enum import GameStates

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
    pubsub.pubsub = pubsub.PubSub()
    pubsub.pubsub.subscribe(pubsub.Subscription(None, pubsub.PubSubTypes.DEATH, on_entity_death))
    pubsub.pubsub.subscribe(pubsub.Subscription(None, pubsub.PubSubTypes.SPAWN, entity_spawn))

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])
    pubsub.pubsub.subscribe(pubsub.Subscription(message_log, pubsub.PubSubTypes.MESSAGE, add_to_messages))

    map_height = constants['map_height']
    map_width = constants['map_width']

    game_map = GameMap()

    player = create_player()

    game_map.create_floor(player, constants)

    game_state = GameStates.PLAYER_TURN

    quest.active_quests = []

    return player, game_map, message_log, game_state

def add_to_messages(sub, message, fov_map, game_map):
    sub.entity.add_message(message.message)

def entity_spawn(sub, message, fov_map, game_map):
    npc = message.entity.spawn.spawn()
    if npc:
        game_map.add_entity_to_map(npc)

def on_entity_death(sub, message, fov_map, game_map):
    pubsub.pubsub.unsubscribe_entity(message.entity)
