import tcod
import random

from tcod.color import Color

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

    'light_door_tile': tcod.orange,
    'dark_door_tile': tcod.darker_orange,

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

    'light_stair_floor': tcod.light_grey,
    'dark_stair_floor':  tcod.grey,

    'light_shallow_water': Color(64, 164, 223),
    'dark_shallow_water': Color(71, 128, 161),

    'light_deep_water': tcod.dark_sea,
    'dark_deep_water': tcod.darkest_sea,

    'light_empty_tile': tcod.black,
    'dark_empty_tile': tcod.black,

    'stairs': tcod.silver,

    'cursor': Color(255, 215, 0),
    'cursor_tail': Color(220, 180, 0),

    'console_background': Color(0, 0, 0),

    'dijkstra_far': Color(0, 0, 255),
    'dijkstra_near': Color(255, 0, 0),

    'elite': tcod.silver,

    'bat': tcod.darker_red,
    'bounty_hunter': tcod.gold,
    'chest': tcod.blue,
    'fungus': Color(117, 225, 117),
    'goblin': tcod.desaturated_green,
    'mimic': tcod.darker_blue,
    'orc': tcod.light_green,
    'player': tcod.darker_green,
    'rat': Color(139, 84, 29),
    'rats_nest': Color(123, 133, 142),
    'snake': Color(89, 152, 47),
    'poisonous_snake': Color(25, 82, 89),
    'snake_egg': tcod.darker_gray,
    'skeleton': tcod.light_blue,
    'troll': tcod.darker_green,
    'necromancer': Color(50, 50, 50),
    'warlord': tcod.black,
    'zombie': Color(145, 145, 0),

    'light_door': tcod.purple,
    'dark_door': tcod.darker_purple,

    'equipment_common': tcod.gray,
    'equipment_uncommon': tcod.chartreuse,
    'equipment_rare': tcod.blue,
    'equipment_epic': tcod.purple,
    'equipment_legendary': tcod.crimson,

    'show_path_track': tcod.silver,
    'show_walkable_path': tcod.lightest_blue,

    'damage_text': tcod.dark_red,
    'death_text': tcod.orange,
    'effect_text': tcod.white,
    'failure_text': tcod.light_red,
    'success_text': tcod.gold,
    'neutral_text': tcod.white,
    'normal_text': tcod.white,

    'quest_available': tcod.white,
    'quest_complete': tcod.blue,
    'quest_ongoing': tcod.silver,

    'species_fiery': tcod.red,
    'species_icy': tcod.blue,
    'species_brass': tcod.brass,
    'species_copper': tcod.copper,
    'species_golden': tcod.gold,

    'corpse': tcod.darkest_red,
    'skeletal': tcod.white,

    'health_near_death': tcod.red,
    'health_injured': tcod.orange,
    'health_barely_injured': tcod.yellow,
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

def random_color_shimmer(color):
    dr = int(random.uniform(-10, 10))
    dg = int(random.uniform(-10, 10))
    db = int(random.uniform(-10, 10))
    red = min(max(0, color.r + dr), 255)
    green = min(max(0, color.g + dg), 255)
    blue = min(max(0, color.b + db), 255)
    return (red, green, blue)
