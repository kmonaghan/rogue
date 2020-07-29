import logging

import tcod

screen_width = 45
info_panel_height = 5
message_panel_height = 10
screen_height = screen_width + 1 + info_panel_height + 1 + message_panel_height

CONFIG = {
    'window_title': 'Yet Another Unnamed Diablo Inspired Roguelike',
    'full_screen_width': screen_width,
    'full_screen_height': screen_height,

    'info_panel_y': screen_height - info_panel_height - message_panel_height + 1,
    'info_panel_height': info_panel_height,
    'message_panel_y': screen_height - message_panel_height,
    'message_panel_height': message_panel_height,
    'message_width': screen_width - 2,
    'message_height': message_panel_height - 2,
    'map_width': screen_width,
    'map_height': screen_width,

    'debug': False,
    'logging_level': logging.INFO,
    'map_generation_attempts': 10,

    'time_between_enemy_turns': 0.03,

    'font': 'data/fonts/Alloy_curses_12x12.png',
    #'font': 'data/fonts/arial10x10.png',
    #'font': 'data/fonts/Unknown_curses_12x12.png',
    #'font_type': tcod.FONT_LAYOUT_TCOD,
    'font_type': tcod.FONT_LAYOUT_ASCII_INROW,

    'cardinal_cost': 2,
    'diagonal_cost': 2,
}
