import tcod

screen_width = 71
screen_height = 56
bar_width = 20
panel_height = 10
info_panel_width = bar_width + 4
message_panel_width = screen_width - info_panel_width

CONFIG = {
    'window_title': 'Diablo inspired Roguelike',
    'full_screen_width': screen_width,
    'full_screen_height': screen_height,

    'bar_width': bar_width,
    'panel_height': panel_height,
    'panel_y': screen_height - panel_height,
    'message_width': message_panel_width - 2,
    'message_height': panel_height - 2,
    'info_panel_width': info_panel_width,
    'message_panel_width': message_panel_width,
    'message_width': message_panel_width - 2,
    'message_height': panel_height - 2,
    'map_width': 45,
    'map_height': screen_height - panel_height - 1,

    'fov_algorithm': tcod.FOV_RESTRICTIVE,
    'fov_light_walls': True,
    'fov_radius': 10,

    'debug': True,
    'show_dijkstra_player': False,
    'show_dijkstra_flee': False,

    'map_generation_attempts': 10,
}
