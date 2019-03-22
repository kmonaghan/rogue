import tcod

from bestiary import create_player

from game_messages import MessageLog

from map_objects.game_map import GameMap

from render_functions import RenderOrder

import pubsub

import quest

from etc.enum import GameStates

def get_constants():
    window_title = 'Diablo inspired Roguelike'

    screen_width = 71
    screen_height = 51

    bar_width = 20
    panel_height = 10
    panel_y = screen_height - panel_height

    info_panel_width = bar_width + 4
    message_panel_width = screen_width - info_panel_width

    message_x = bar_width + 2
    message_width = message_panel_width - 2
    message_height = panel_height - 2

    map_width = screen_width
    map_height = screen_height - panel_height - 1

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = tcod.FOV_RESTRICTIVE
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    constants = {
        'window_title': window_title,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'info_panel_width': info_panel_width,
        'message_panel_width': message_panel_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room
    }

    return constants


def get_game_variables(constants):
    pubsub.pubsub = pubsub.PubSub()
    pubsub.pubsub.subscribe(pubsub.Subscription(None, pubsub.PubSubTypes.DEATH, on_entity_death))
    pubsub.pubsub.subscribe(pubsub.Subscription(None, pubsub.PubSubTypes.SPAWN, entity_spawn))

    message_log = MessageLog(constants['message_width'], constants['message_height'])
    pubsub.pubsub.subscribe(pubsub.Subscription(message_log, pubsub.PubSubTypes.MESSAGE, add_to_messages))

    game_map = GameMap()

    player = create_player()

    game_state = GameStates.PLAYER_TURN

    quest.active_quests = []

    return player, game_map, message_log, game_state

def add_to_messages(sub, message, game_map):
    sub.entity.add_message(message.message)

def entity_spawn(sub, message, game_map):
    npc = message.entity.spawn.spawn()
    if npc:
        game_map.current_level.add_entity(npc)

def on_entity_death(sub, message, game_map):
    pubsub.pubsub.unsubscribe_entity(message.entity)
