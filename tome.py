from random import randint

import numpy as np

from components.ai import ConfusedNPC

from map_objects.point import Point

from game_messages import Message

from utils.random_utils import die_roll

from etc.enum import DamageType, ResultTypes
from etc.colors import COLORS

#spell values
HEAL_AMOUNT = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3

def heal(*args, **kwargs):
    entity = args[0]
    number_of_die = kwargs.get('number_of_die')
    type_of_die = kwargs.get('type_of_die')
    target = kwargs.get('target')

    results = []

    if entity.health.hp == entity.health.max_hp:
        results.append({ResultTypes.MESSAGE: Message('You are already at full health', COLORS.get('neutral_text'))})
    else:
        entity.health.heal(die_roll(number_of_die, type_of_die))
        results.append({ResultTypes.MESSAGE: Message('Your wounds start to feel better!', COLORS.get('success_text'))})

    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    game_map = kwargs.get('game_map')
    number_of_die = kwargs.get('number_of_die')
    type_of_die = kwargs.get('type_of_die')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in game_map.current_level.entities:
        if entity.fighter and entity != caster and game_map.current_level.fov[entity.x, entity.y]:
            distance = caster.point.distance_to(entity.point)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        damage = die_roll(number_of_die, type_of_die)
        results.extend({ResultTypes.MESSAGE: Message('A lighting bolt strikes the {0} with a loud thunder!'.format(target.name), COLORS.get('effect_text'))})
        results.extend(target.health.take_damage(damage, caster, DamageType.ELECTRIC))
    else:
        results.append({ResultTypes.MESSAGE: Message('No enemy is close enough to strike.', COLORS.get('failure_text'))})

    return results

def cast_fireball(*args, **kwargs):
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    number_of_die = kwargs.get('number_of_die')
    type_of_die = kwargs.get('type_of_die')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not game_map.current_level.fov[target_x, target_y]:
        results.append({ResultTypes.MESSAGE: Message('You cannot target a tile outside your field of view.', COLORS.get('neutral_text'))})
        return results

    results.append({ResultTypes.MESSAGE: Message('The fireball explodes, burning everything within {0} tiles!'.format(radius), COLORS.get('effect_text'))})

    #TODO: refactor, this is probably horribly inefficent
    for entity in game_map.current_level.entities:
        if entity.point.distance_to(Point(target_x, target_y)) <= radius and entity.health:
            damage = die_roll(number_of_die, type_of_die)
            results.extend(entity.health.take_damage(damage, caster, DamageType.FIRE))

    return results

def cast_confuse(*args, **kwargs):
    game_map = kwargs.get('game_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not game_map.current_level.fov[target_x, target_y]:
        results.append({ResultTypes.MESSAGE: Message('You cannot target a tile outside your field of view.', COLORS.get('neutral_text'))})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedNPC(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({ResultTypes.MESSAGE: Message('The eyes of the {0} look vacant, as he starts to stumble around!'.format(entity.name), COLORS.get('effect_text'))})

            break
    else:
        results.append({ResultTypes.MESSAGE: Message('There is no targetable enemy at that location.', COLORS.get('neutral_text'))})

    return results

def cast_summon_npc(point, ncp_type, game_map, number_of_npc=6):
    dice = randint(1, number_of_npc)

    start_x = point.x - 1
    start_y = point.y - 1

    offset = 3

    if (start_x < 0):
        start_x = 0
        offset = 2

    if (start_y < 0):
        start_y = 0
        offset = 2

    for x in range(start_x, start_x + offset):
        for y in range(start_y, start_y + offset):
            if not game_map.current_level.blocked[x, y]:
                npc = ncp_type(Point(x, y))
                game_map.current_level.add_entity(npc)
                dice -= 1

                if dice < 1:
                    return

def resurrect_all_npc(npc_type, game_map, target):
    for entity in game_map.entities:
        if entity.health and entity.health.dead:
            npc_type(entity)
    return

def cast_teleport(*args, **kwargs):
    game_map = kwargs.get('game_map')
    caster = kwargs.get('caster')

    results = []

    point = game_map.current_level.find_random_open_position()
    caster.movement.place(point.x, point.y, game_map.current_level)

    results.append({ResultTypes.MESSAGE: Message('You feel like you are torn apart and put back together again.', COLORS.get('success_text'))})
    results.append({ResultTypes.FOV_RECOMPUTE: True})

    return results

def cast_mapping(*args, **kwargs):
    game_map = kwargs.get('game_map')

    results = []

    game_map.current_level.explored = np.full(game_map.current_level.grid.shape, 1, dtype=np.int8)

    results.append({ResultTypes.MESSAGE: Message('The scroll contains a map of immediate area.', COLORS.get('success_text'))})
    results.append({ResultTypes.FOV_RECOMPUTE: True})

    return results

def cast_identify(*args, **kwargs):
    target = kwargs.get('target')

    results = []

    if target.identifiable and not target.identified:
        target.identifiable.identified = True

    results.append({ResultTypes.MESSAGE: Message(f"The item is a {target.name}", COLORS.get('effect_text'))})

    return results
