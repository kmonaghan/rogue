import logging

from random import randint, shuffle

import numpy as np

import bestiary

from components.ai import (BasicNPC, ConfusedNPC)
from components.speed import Speed

from map_objects.point import Point

from game_messages import Message

from utils.random_utils import die_roll

from etc.enum import DamageType, MessageType, ResultTypes
from etc.colors import COLORS

def antidote(*args, **kwargs):
    target = kwargs.get('target')

    results = []

    if target.poisoned:
        results.extend(target.poisoned.end())

    results.append({ResultTypes.MESSAGE: Message(f"{target.name} feels clensed.", COLORS.get('success_text'), target=target, type=MessageType.EFFECT)})

    return results

def confuse(*args, **kwargs):
    game_map = kwargs.get('game_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not game_map.current_level.fov[target_x, target_y]:
        results.append({ResultTypes.MESSAGE: Message('You cannot target a tile outside your field of view.', COLORS.get('neutral_text'))})
        return results

    entities = game_map.current_level.entities.get_entities_in_position((target_x, target_y))
    for entity in entities:
        if entity.ai:
            confused_ai = ConfusedNPC(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({ResultTypes.MESSAGE: Message('The eyes of the {0} look vacant and they start to stumble around!'.format(entity.name), COLORS.get('effect_text'), target=entity, type=MessageType.EFFECT)})

            break
    else:
        results.append({ResultTypes.MESSAGE: Message('There is no targetable enemy at that location.', COLORS.get('neutral_text'))})

    return results

def change_defence(*args, **kwargs):
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    caster = kwargs.get('caster')
    target = kwargs.get('target')

    results = []

    extra = die_roll(number_of_dice, type_of_dice)
    logging.info(f"adding {extra} to base power from {number_of_dice}d{type_of_dice}")
    target.defence.base_defence = target.defence.base_defence + extra
    results.append({ResultTypes.MESSAGE: Message('You feel more secure in yourself!', COLORS.get('success_text'), target=target, type=MessageType.EFFECT)})

    return results

def change_power(*args, **kwargs):
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    caster = kwargs.get('caster')
    target = kwargs.get('target')

    results = []

    extra = die_roll(number_of_dice, type_of_dice)
    logging.info(f"adding {extra} to base power from {number_of_dice}d{type_of_dice}")
    target.offence.base_power = target.offence.base_power + extra
    results.append({ResultTypes.MESSAGE: Message('You feel like you can take anything on!', COLORS.get('success_text'))})

    return results

def fireball(*args, **kwargs):
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
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
            damage = die_roll(number_of_dice, type_of_dice)
            damage_results, total_damage = entity.health.take_damage(damage, caster, DamageType.FIRE)
            results.extend(damage_results)

    return results

def heal(*args, **kwargs):
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    caster = kwargs.get('caster')
    target = kwargs.get('target')

    results = []

    if target.health.hp == target.health.max_hp:
        results.append({ResultTypes.MESSAGE: Message(f"{target.name} is already at full health.", COLORS.get('neutral_text'), target=target, type=MessageType.EFFECT)})
    else:
        target.health.heal(die_roll(number_of_dice, type_of_dice))
        results.append({ResultTypes.MESSAGE: Message(f"{target.name} wounds start to close up.", COLORS.get('success_text'), target=target, type=MessageType.EFFECT)})

    return results

def identify(*args, **kwargs):
    target = kwargs.get('target')

    results = []

    if target.identifiable and not target.identified:
        target.identifiable.identified = True

    results.append({ResultTypes.MESSAGE: Message(f"The item is a {target.name}", COLORS.get('effect_text'))})
    if target.identifiable.common_ident:
        results.append({ResultTypes.COMMON_IDENT: target.base_name})

    return results

def lightning(*args, **kwargs):
    caster = kwargs.get('caster')
    target = kwargs.get('target')
    game_map = kwargs.get('game_map')
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    radius = kwargs.get('radius')

    results = []
    targets = []

    start_x = max(0, caster.x - radius)
    start_y = max(0, caster.y - radius)

    end_x = min(caster.x + radius, game_map.current_level.width)
    end_y = min(caster.y + radius, game_map.current_level.width)

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            entities = game_map.current_level.entities.get_entities_in_position((x,y))
            for entity in entities:
                if entity == caster:
                    continue
                if not entity.health:
                    continue
                if entity.health.dead:
                    continue

                targets.append(entity)

    if target:
        targets.insert(0, target)

    if targets:
        total_targets = min(len(target), number_of_dice)
        for _ in range(total_targets):
            target = targets.pop()
            damage = die_roll(1, type_of_dice)
            if i > 0:
                results.append({ResultTypes.MESSAGE: Message(f"The bolt bounces and strikes {target.name} with a loud crack of thunder!", COLORS.get('effect_text'), target=target, type=MessageType.EFFECT)})
            else:
                results.append({ResultTypes.MESSAGE: Message(f"A lighting bolt strikes the {target.name} with a loud crack of thunder!", COLORS.get('effect_text'), target=target, type=MessageType.EFFECT)})

            damage_results, total_damage = target.health.take_damage(damage, caster, DamageType.ELECTRIC)
            results.append({ResultTypes.MESSAGE: Message(f"{target.name} takes {str(total_damage)} damage.", COLORS.get('damage_text'))})
            results.extend(damage_results)
    else:
        results.append({ResultTypes.MESSAGE: Message("No enemy is close enough to strike.", COLORS.get('failure_text'))})

    return results

def mapping(*args, **kwargs):
    game_map = kwargs.get('game_map')

    results = []

    game_map.current_level.explored = np.full(game_map.current_level.grid.shape, 1, dtype=np.int8)

    results.append({ResultTypes.MESSAGE: Message('The scroll contains a map of immediate area.', COLORS.get('success_text'))})
    results.append({ResultTypes.FOV_RECOMPUTE: True})

    return results

def summon_npc(point, ncp_type, game_map, number_of_npc=6):
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

def speed(*args, **kwargs):
    caster = kwargs.get('caster')
    target = kwargs.get('target')

    results = []

    target.add_component(Speed(), 'speed')
    target.speed.start()
    results.append({ResultTypes.MESSAGE: Message(f"{target.name} speeds up", COLORS.get('effect_text'), target=target, type=MessageType.EFFECT)})

    return results

def teleport(*args, **kwargs):
    game_map = kwargs.get('game_map')
    caster = kwargs.get('caster')

    results = []

    point = game_map.current_level.find_random_open_position()
    orginal_point = caster.point
    caster.movement.place(point.x, point.y, game_map.current_level)

    results.append({ResultTypes.MESSAGE: Message('You feel like you are torn apart and put back together again.', COLORS.get('success_text'))})
    results.append({ResultTypes.FOV_RECOMPUTE: True})

    chance_of_teleport_going_wrong = randint(1, 100)

    if (chance_of_teleport_going_wrong >= 99):
        clone = bestiary.create_player()
        clone_point = game_map.current_level.find_random_open_position()
        clone.set_point(clone_point)
        clone.char = 'C'
        clone.base_name = 'Clone of ' + clone.base_name
        clone.add_component(BasicNPC(), 'ai')
        clone.ai.set_target(caster)
        clone.ai.tree.namespace["target_point"] = caster.point
        game_map.current_level.add_entity(clone)
        results.append({ResultTypes.MESSAGE: Message(f"You feel as if you are split in two.", COLORS.get('damage_text'))})

    elif (chance_of_teleport_going_wrong >= 90):
        damage_results, total_damage = caster.health.take_damage(die_roll(1, 6, int(orginal_point.distance_to(point))))
        results.append({ResultTypes.MESSAGE: Message(f"You take {str(total_damage)} damage.", COLORS.get('damage_text'))})
        results.extend(damage_results)

    return results

def resurrect_all_npc(npc_type, game_map, target):
    for entity in game_map.entities:
        if entity.health and entity.health.dead:
            npc_type(entity)
    return
