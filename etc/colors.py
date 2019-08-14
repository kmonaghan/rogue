import tcod

COLORS = {
    'light_default': tcod.dark_grey,
    'dark_default': tcod.darkest_grey,

    'light_cavern_floor': tcod.lighter_sepia,
    'dark_cavern_floor': tcod.light_sepia,

    'dark_wall': tcod.darkest_sepia,
    'dark_ground': tcod.darker_sepia,
    'light_wall': tcod.dark_sepia,
    'light_ground': tcod.sepia,

    'light_cavern_wall': tcod.dark_sepia,
    'dark_cavern_wall': tcod.darkest_sepia,

    'light_door': tcod.orange,
    'dark_door': tcod.darker_orange,

    'light_impenetrable': tcod.red,
    'dark_impenetrable': tcod.darker_red,

    'light_room_floor': tcod.light_grey,
    'dark_room_floor': tcod.grey,

    'light_corridor_floor': tcod.sepia,
    'dark_corridor_floor': tcod.darker_sepia,

    'light_potential_corridor_floor': tcod.lightest_green,
    'dark_potential_corridor_floor': tcod.lightest_green,

    'light_room_wall': tcod.dark_grey,
    'dark_room_wall': tcod.darkest_grey,

    'light_stair_floor': tcod.light_yellow,
    'dark_stair_floor':  tcod.yellow,

    'light_shallow_water': tcod.lighter_blue,
    'dark_shallow_water': tcod.light_blue,

    'light_deep_water': tcod.dark_blue,
    'dark_deep_water': tcod.darkest_blue,

    'light_empty_tile': tcod.black,
    'dark_empty_tile': tcod.black,

    'stairs': tcod.silver,

    'goblin': (46, 139, 87),
    'orc': (46, 139, 87),
    'troll': (128, 128, 0),
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
