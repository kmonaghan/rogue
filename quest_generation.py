import logging
from random import choice, randint

import bestiary
import quest

from etc.enum import RoutingOptions, Species, Tiles, HUMANOIDS, VERMIN_GENERATORS

def kill_vermin():
    key, value = choice(list(VERMIN_GENERATORS.items()))
    title = "The Verminator"
    description = f"These caves are riddled with vermin. Clear out the {value}s."

    q = quest.Quest(title, description, 100)
    q.kill = randint(2,5)
    q.kill_type = key
    q.return_to_quest_giver = True

    return q

def kill_humanoid(type = None):
    if not type:
        type, value = choice(list(HUMANOIDS.items()))
    else:
        value = HUMANOIDS[type]

    title = f"Tread on the {value}s."
    description = f"There is an awful lot of {value} in here. Get rid of them. I don't care how."

    q = quest.Quest(title, description, 100)
    q.kill = randint(2,5)
    q.kill_type = type
    q.return_to_quest_giver = True

    return q

def kill_mini_boss(npc, room_name = None):
    quest_text = f"Elimate the local problem: {npc.name}."

    if room_name:
        quest_text = quest_text + f" You'll find them in {room_name}."

    q1 = quest.Quest("Cut off the head", quest_text, 100, target_npc=npc)


def kill_warlord():
    title = "Strike him down"
    description = "Time to take down the king of the hill. Or dungeon as it is in this case."

    q = quest.Quest(title, description, 500)
    q.kill = 1
    q.kill_type = "warlord"
    q.return_to_quest_giver = True

    return q

def generate_quest_chain(game_map, npc = None, room_name = None):
    if game_map.dungeon_level == 1:
        return level_one_chain(game_map)

    return prefab_chain(game_map, dungeon_level, npc, room_name)

def level_one_chain(game_map):
    q1 = kill_vermin()
    q2 = quest.Quest('Interloper',
                        'Someone has been sneaking around here. Find them and take care of it.',
                        100,
                        start_func=level_one_goblin)
    q2.kill = 1
    q2.kill_type = Species.GOBLIN

    q1.next_quest = q2

    q2.next_quest = exit_level_quest(game_map)

    return q1

def prefab_chain(game_map, npc, room_name = None):
    q1 = kill_humanoid()

    q2 = kill_mini_boss(npc, room_name)

    if game_map.down_stairs:
        q2.next_quest = exit_level_quest(game_map)
    else:
        logging.info("No stairs down")

    return q1

def exit_level_quest(game_map):
    return quest.Quest('Ever deeper we go...',
                        'More adventure awaits if you go deeper into the depths of this accursed place.',
                        100,
                        map_point = game_map.down_stairs.point)

def level_one_goblin(game_map):
    point = game_map.current_level.find_random_open_position([Tiles.CORRIDOR_FLOOR,
                                                                Tiles.DOOR,
                                                                Tiles.ROOM_FLOOR,
                                                                Tiles.STAIRS_FLOOR,
                                                                RoutingOptions.AVOID_FOV])

    game_map.current_level.add_entity(bestiary.generate_npc(Species.GOBLIN, 1, 1, point))
