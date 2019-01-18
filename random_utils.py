import tcod as libtcod

from random import randint

def from_dungeon_level(table, dungeon_level):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value

    return 0


def random_choice_index(chances):
    random_chance = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if random_chance <= running_sum:
            return choice
        choice += 1


def random_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())

    return choices[random_choice_index(chances)]

def die_roll(number_of_dice=1, type_of_dice=1, bonus=0):
    total = 0

    for x in range(0, number_of_dice):
        total += libtcod.random_get_int(0, 1, type_of_dice)

    return total + bonus
