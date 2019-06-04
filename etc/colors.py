import tcod

COLORS = {
    'dark_wall': tcod.darkest_sepia,
    'dark_ground': tcod.darker_sepia,
    'light_wall': tcod.dark_sepia,
    'light_ground': tcod.sepia,

    'stairs': tcod.silver,

    'orc': (46, 139, 87),
    'troll': (128, 128, 0),
    'kruthik': (160, 82, 45),
    'pink_jelly': (255, 20, 147),
    'fire_bloat': (240, 0, 0),
    'water_bloat': (140, 140, 255),
    'zombie': (145, 145, 0),
    'necromancer': (50, 50, 50),

    'cursor': (255, 215, 0),
    'cursor_tail': (220, 180, 0),

    'console_background': (0, 0, 0),

    'dijkstra_far': (0, 0, 255),
    'dijkstra_near': (255, 0, 0),
}

STATUS_BAR_COLORS = {
    'hp_bar': {
        'bar_color': tcod.light_red,
        'back_color': tcod.darker_red,
        'string_color': tcod.white
    },
    'xp_bar': {
        'bar_color': tcod.light_blue,
        'back_color': tcod.darker_blue,
        'string_color': tcod.white
    }
}
