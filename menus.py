import libtcodpy as libtcod

import quest

def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text, color in options:
        libtcod.console_set_default_foreground(window, color)
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def inventory_menu(con, header, player, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(player.inventory.items) == 0:
        options = [['Inventory is empty.', libtcod.white]]
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append(['{0} (carried in main hand)'.format(item.name), item.color])
            elif player.equipment.off_hand == item:
                options.append(['{0} (carried in off hand)'.format(item.name), item.color])
            elif player.equipment.chest == item:
                options.append(['{0} (worn on chest)'.format(item.name), item.color])
            elif player.equipment.head == item:
                options.append(['{0} (worn on head)'.format(item.name), item.color])
            elif player.equipment.left_ring_finger == item:
                options.append(['{0} (worn on left hand)'.format(item.name), item.color])
            elif player.equipment.right_ring_finger == item:
                options.append(['{0} (worn on right hand)'.format(item.name), item.color])
            else:
                options.append([item.name, item.color])

    menu(con, header, options, inventory_width, screen_width, screen_height)

def quest_menu(con, header, quest, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    header = quest.title + "\n" + quest.description
    options = [['Let\'s go do it!', libtcod.white],
                ['Not right now', libtcod.white]]

    menu(con, header, options, inventory_width, screen_width, screen_height)

def quest_list_menu(con, header, player, inventory_width, screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(quest.active_quests) == 0:
        options = [['No active quests.', libtcod.white]]
    else:
        options = []

        for q in quest.active_quests:
            options.append([q.title, libtcod.white])

    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height):
    #libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                             'TOMBS OF THE ANCIENT KINGS')
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), libtcod.BKGND_NONE, libtcod.CENTER,
                             'By Karl Monaghan')

    menu(con, '', [['Play a new game', libtcod.white], ['Continue last game', libtcod.white], ['Quit', libtcod.white]], 24, screen_width, screen_height)


def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    options = [['Constitution (+20 HP, from {0})'.format(player.health.max_hp), libtcod.white],
               ['Strength (+1 attack, from {0})'.format(player.offence.power), libtcod.white],
               ['Agility (+1 defence, from {0})'.format(player.defence.defence), libtcod.white]]

    menu(con, header, options, menu_width, screen_width, screen_height)


def character_screen(player, character_screen_width, character_screen_height, screen_width, screen_height):
    window = libtcod.console_new(character_screen_width, character_screen_height)

    libtcod.console_set_default_foreground(window, libtcod.white)

    libtcod.console_print_rect_ex(window, 0, 1, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Character Information')
    libtcod.console_print_rect_ex(window, 0, 2, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Level: {0}'.format(player.level.current_level))
    libtcod.console_print_rect_ex(window, 0, 3, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Experience: {0}'.format(player.level.current_xp))
    libtcod.console_print_rect_ex(window, 0, 4, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Experience to Level: {0}'.format(player.level.experience_to_next_level))
    libtcod.console_print_rect_ex(window, 0, 6, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Maximum HP: {0}'.format(player.health.max_hp))
    libtcod.console_print_rect_ex(window, 0, 7, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Attack: {0}'.format(player.offence.power))
    libtcod.console_print_rect_ex(window, 0, 8, character_screen_width, character_screen_height, libtcod.BKGND_NONE,
                                  libtcod.LEFT, 'Defense: {0}'.format(player.defence.defence))

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    libtcod.console_blit(window, 0, 0, character_screen_width, character_screen_height, 0, x, y, 1.0, 0.7)

def game_completed(con, menu_width, screen_width, screen_height):
    header = 'Congratulations - You have defeated the King Under the Hill'
    options = [['Restart with higher level encounters', libtcod.white],
                ['Start from scratch', libtcod.white],
                ['Quit while the going is good', libtcod.white]]

    menu(con, header, options, menu_width, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
