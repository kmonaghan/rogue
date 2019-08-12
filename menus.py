import tcod

import quest

def menu(con, header, options, width, screen_width, screen_height):
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

def menu2(title, header, options, width, screen_width, screen_height):
    header_height = 2 #tcod.console_get_height_rect(con, 0, 0, width - 2, screen_height, header)
    height = len(options) + header_height + 1

    text = ''
    letter_index = ord('a')
    for option_text, color in options:
        text += '(' + chr(letter_index) + ') ' + option_text + "\n"
        letter_index += 1

    con = tcod.console.Console(width, height + 5, 'F')

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
        1,
        con.width - 2,
        header_height,
        header,
        fg=tcod.white,
        bg=None,
        alignment=tcod.LEFT,
    )

    con.draw_rect(1, header_height+1, con.width - 2, 1, ord('_'), tcod.white)

    con.print_box(
        1,
        header_height + 3,
        con.width - 2,
        len(options),
        text,
        fg=tcod.white,
        bg=None,
        alignment=tcod.LEFT,
    )

    return con

def inventory_menu(header, player, width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(player.inventory.items) == 0:
        options = [['Inventory is empty.', tcod.white]]
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append(['{0} (in main hand)'.format(item.name), item.color])
            elif player.equipment.off_hand == item:
                options.append(['{0} (in off hand)'.format(item.name), item.color])
            elif player.equipment.chest == item:
                options.append(['{0} (on chest)'.format(item.name), item.color])
            elif player.equipment.head == item:
                options.append(['{0} (on head)'.format(item.name), item.color])
            elif player.equipment.left_ring_finger == item:
                options.append(['{0} (on left hand)'.format(item.name), item.color])
            elif player.equipment.right_ring_finger == item:
                options.append(['{0} (on right hand)'.format(item.name), item.color])
            else:
                options.append([item.name, item.color])

    return menu2('Inventory', header, options, width, screen_width, screen_height)

def quest_menu(header, quest, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    header = quest.title + "\n" + quest.description
    options = [['Let\'s go do it!', tcod.white],
                ['Not right now', tcod.white]]

    return menu2('Quest', header, options, inventory_width, screen_width, screen_height)

def quest_list_menu(header, player, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(quest.active_quests) == 0:
        options = [['No active quests.', tcod.white]]
    else:
        options = []

        for q in quest.active_quests:
            options.append([q.title, tcod.white])

    return menu2('Quest', header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height):
    #tcod.image_blit_2x(background_image, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.light_yellow)
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, tcod.BKGND_NONE, tcod.CENTER,
                             'Diablo inspired Roguelike')
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), tcod.BKGND_NONE, tcod.CENTER,
                             'By Karl Monaghan')

    menu(con, '', [['Play a new game', tcod.white], ['Continue last game', tcod.white], ['Quit', tcod.white]], 24, screen_width, screen_height)


def level_up_menu(header, player, menu_width, screen_width, screen_height):
    options = [['Constitution (+20 HP, from {0})'.format(player.health.max_hp), tcod.white],
               ['Strength (+1 attack, from {0})'.format(player.offence.power), tcod.white],
               ['Agility (+1 defence, from {0})'.format(player.defence.defence), tcod.white]]

    return menu2('Quest', header, options, menu_width, screen_width, screen_height)


def character_screen(player, character_screen_width, character_screen_height, screen_width, screen_height):
    options =['Level: {0}'.format(player.level.current_level),
                'Experience: {0}'.format(player.level.current_xp),
                'Experience to Level: {0}'.format(player.level.experience_to_next_level),
                'Maximum HP: {0}'.format(player.health.max_hp),
                'Attack: {0}'.format(player.offence.power),
                'Defence: {0}'.format(player.defence.defence),
            ]

    height = len(options) + 2

    con = tcod.console.Console(character_screen_width, height, 'F')

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

def game_over(menu_width, screen_width, screen_height):
    header = "You have failed. Death's cold embrace envelops you. Loser."
    options = [['Start from scratch', tcod.white],
                ['View Stats', tcod.white],
                ['View Inventory', tcod.white],
                ['View Quests', tcod.white],
                ['Quit', tcod.white]]

    return menu2('Quest', header, options, menu_width, screen_width, screen_height)

def game_paused(menu_width, screen_width, screen_height):
    header = ""
    options = [['Restart', tcod.white],
                ['Save Game', tcod.white],
                ['Quit', tcod.white]]

    return menu2('Paused', header, options, menu_width, screen_width, screen_height)

def game_completed(menu_width, screen_width, screen_height):
    header = 'Congratulations - You have defeated the King Under the Hill'
    options = [['Restart with higher level encounters', tcod.white],
                ['Start from scratch', tcod.white],
                ['Quit while the going is good', tcod.white]]

    return menu2('Game Complete', header, options, menu_width, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
