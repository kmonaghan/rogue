import tcod

screen_width = 45
screen_height = 60
info_panel_height = 5
message_panel_height = 10

CONFIG = {
    'window_title': 'Diablo inspired Roguelike',
    'full_screen_width': screen_width,
    'full_screen_height': screen_height,

    'info_panel_y': screen_height - info_panel_height - message_panel_height,
    'info_panel_height': info_panel_height,
    'message_panel_y': screen_height - message_panel_height,
    'message_panel_height': message_panel_height,
    'message_width': screen_width - 2,
    'message_height': message_panel_height - 2,
    'map_width': 45,
    'map_height': 45,

    'fov_algorithm': tcod.FOV_RESTRICTIVE,
    'fov_light_walls': True,
    'fov_radius': 10,

    'debug': False,
    'show_dijkstra_player': False,
    'show_dijkstra_flee': False,

    'map_generation_attempts': 10,
}
