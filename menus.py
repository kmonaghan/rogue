import tcod

import quest

from etc.colors import COLORS
from etc.configuration import CONFIG

def menu(con, header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tcod.console_new(width, height)

    # print the header, with auto-wrap
    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text, color in options:
        tcod.console_set_default_foreground(window, color)
        text = '(' + chr(letter_index) + ') ' + option_text
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def ingame_menu(title, header, options):
    con = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')

    header_height = con.get_height_rect(1, 1, con.width - 2, 10, header) + 1
    con.draw_frame(
        0,
        0,
        con.width,
        con.height,
        title,
        False,
        fg=tcod.white,
        bg=tcod.black,
    )

    con.print_box(
        1,
        2,
        con.width - 2,
        header_height,
        header,
        fg=tcod.white,
        bg=None,
        alignment=tcod.LEFT,
    )

    con.draw_rect(1, header_height+1, con.width - 2, 1, ord('_'), tcod.white)

    current_y = header_height + 3
    letter_index = ord('a')
    for option_text, color in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        letter_index += 1
        text_height = con.get_height_rect(1, current_y, con.width - 2, 10, text)

        con.print_box(
            1,
            current_y,
            con.width - 2,
            text_height,
            text,
            fg=color,
            bg=None,
            alignment=tcod.LEFT,
        )

        current_y = current_y + text_height

    return con

def inventory_menu(header, player, exclude = []):
    # show a menu with each item of the inventory as an option
    if len(player.inventory.items) == 0:
        options = [['Inventory is empty.', tcod.white]]
    else:
        options = []

        current_items = player.inventory.items.copy()
        for item in exclude:
            current_items.remove(item)

        for item in current_items:
            formated_name = item.name
            if player.equipment.main_hand == item:
                formated_name += ' (in main hand)'
            elif player.equipment.off_hand == item:
                formated_name += ' (in off hand)'
            elif player.equipment.chest == item:
                formated_name += ' (on chest)'
            elif player.equipment.head == item:
                formated_name += ' (on head)'
            elif player.equipment.left_ring_finger == item:
                formated_name += ' (on left hand)'
            elif player.equipment.right_ring_finger == item:
                formated_name += ' (on right hand)'

            if item.identifiable and not item.identifiable.identified:
                item_colour = tcod.red
                formated_name += ' (identifiable)'
            else:
                item_colour = item.color

            options.append([formated_name, item_colour])

    return ingame_menu('Inventory', header, options)

def quest_menu(quest):
    title = 'Quest'
    header = quest.title + "\n" + quest.description
    options = [['Let\'s go do it!', tcod.white],
                ['Not right now', tcod.white]]

    return ingame_menu(title, header, options)

def quest_list_menu(player):
    title = 'Current Quests'
    header = 'Press the key next to an quest to get details, or Esc to cancel.'
    # show a menu with each item of the inventory as an option
    if len(quest.active_quests) == 0:
        options = [['No active quests.', tcod.white]]
    else:
        options = []

        for q in quest.active_quests:
            options.append([q.title, tcod.white])

    return ingame_menu(title, header, options)

def main_menu(con, background_image):
    #tcod.image_blit_2x(background_image, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.light_yellow)
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, tcod.BKGND_NONE, tcod.CENTER,
                             'Diablo inspired Roguelike')
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), tcod.BKGND_NONE, tcod.CENTER,
                             'By Karl Monaghan')

    menu(con, '', [['Play a new game', tcod.white], ['Continue last game', tcod.white], ['Quit', tcod.white]], 24, screen_width, screen_height)

def level_up_menu(player):
    title = 'Level up!'
    header = 'You\'ve earned enough XP to level up. Pick a stat to increase.'
    options = [[f"Constitution +20 HP (from {player.health.max_hp} to {player.health.max_hp + 20})", tcod.white],
               [f"Strength +1 attack (from {player.offence.power} to {player.offence.power + 1})", tcod.white],
               [f"Agility +1 defence (from {player.defence.defence} to {player.defence.defence + 1})", tcod.white]]

    return ingame_menu(title, header, options)

def character_screen(player):
    options =['Level: {0}'.format(player.level.current_level),
                'Experience: {0}'.format(player.level.current_xp),
                'Experience to Level: {0}'.format(player.level.experience_to_next_level),
                'Maximum HP: {0}'.format(player.health.max_hp),
                'Attack: {0}'.format(player.offence.power),
                'Defence: {0}'.format(player.defence.defence),
            ]

    height = len(options) + 2

    con = tcod.console.Console(CONFIG.get('map_width'), height, 'F')

    con.draw_frame(
        0,
        0,
        con.width,
        con.height,
        'Character Profile',
        False,
        fg=tcod.white,
        bg=tcod.black,
    )

    con.print_box(
        1,
        1,
        con.width - 2,
        len(options),
        '\n'.join(options),
        fg=tcod.white,
        bg=None,
        alignment=tcod.LEFT,
    )

    return con

def game_over():
    header = "You have failed. Death's cold embrace envelops you."
    options = [['Start from scratch', tcod.white],
                ['View Stats', tcod.white],
                ['View Inventory', tcod.white],
                ['View Quests', tcod.white],
                ['Quit', tcod.white]]

    return ingame_menu('Quest', header, options)

def game_paused():
    header = ""
    options = [['Restart', tcod.white],
                ['Save Game', tcod.white],
                ['Quit', tcod.white]]

    return ingame_menu('Paused', header, options)

def game_completed():
    header = 'Congratulations - You\'ve defeated the warlord'
    options = [['Restart with higher level encounters', tcod.white],
                ['Start from scratch', tcod.white],
                ['Quit while the going is good', tcod.white]]

    return ingame_menu('Victory!', header, options)

def message_box(con, header):
    menu(con, header, [], width)
