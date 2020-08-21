import logging

from random import randint, shuffle

import numpy as np

import bestiary

from components.ai import (BasicNPC, ConfusedNPC)
from components.speed import Speed

from entities.character import Character

from map_objects.point import Point

from game_messages import Message

from utils.random_utils import die_roll
from utils.utils import bresenham_line, bresenham_ray

from etc.enum import DamageType, MessageType, ResultTypes
from etc.colors import COLORS

def antidote(**kwargs):
    '''Cast antidote.

    Remove poisoned component from an entity (if it exists).

    Parameters
    ----------
    kwargs:
       target (Entity): The entity that is being targetted by the spell.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    target = kwargs.get('target')

    results = []

    if target.poisoned:
        results.extend(target.poisoned.end())

    results.append({ResultTypes.MESSAGE: Message(f"{target.name} feels clensed.", COLORS.get('success_text'), target=target, type=MessageType.EFFECT)})

    return results

def chain_lightning(**kwargs):
    '''Cast chain lightning.

    Does ELECTRIC damage to a max of [number_of_dice] entities within a [radius].
    Each entity recieves 1D[type_of_dice] damage.

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       game_map (GameMap): Current game map.
       number_of_dice (int): number of die to roll.
       radius (int): radius of the spell effect.
       target_x (int): x co-ordinate.
       target_y (int): y co-ordinate.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    number_of_dice = kwargs.get('number_of_dice')
    radius = kwargs.get('radius')
    target = kwargs.get('target')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    type_of_dice = kwargs.get('type_of_dice')

    results = []
    targets = []

    if (not target_x) and target:
        target_x = target.x
        target_y = target.y

    start_x = max(0, target_x - radius)
    start_y = max(0, target_y - radius)

    end_x = min(target_x + radius, game_map.current_level.width)
    end_y = min(target_y + radius, game_map.current_level.width)

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

    if targets:
        total_targets = min(len(targets), number_of_dice)
        for i in range(total_targets):
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

def change_defence(**kwargs):
    '''Cast change defence.

    Update an entity's defence by [number_of_dice]D[type_of_dice].

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       number_of_dice (int): number of die to roll.
       target (Entity): The entity that is being targetted by the spell.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    number_of_dice = kwargs.get('number_of_dice')
    target = kwargs.get('target')
    type_of_dice = kwargs.get('type_of_dice')

    results = []

    extra = die_roll(number_of_dice, type_of_dice)
    target.defence.base_defence = target.defence.base_defence + extra
    results.append({ResultTypes.MESSAGE: Message('You feel more secure in yourself!', COLORS.get('success_text'), target=target, type=MessageType.EFFECT)})

    return results

def change_power(**kwargs):
    '''Cast increase power.

    Update an entity's power by [number_of_dice]D[type_of_dice].

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       number_of_dice (int): number of die to roll.
       target (Entity): The entity that is being targetted by the spell.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    number_of_dice = kwargs.get('number_of_dice')
    target = kwargs.get('target')
    type_of_dice = kwargs.get('type_of_dice')

    results = []

    extra = die_roll(number_of_dice, type_of_dice)
    target.offence.base_power = target.offence.base_power + extra
    results.append({ResultTypes.MESSAGE: Message('You feel like you can take anything on!', COLORS.get('success_text'))})

    return results

def confuse(**kwargs):
    '''Cast confuse.

    Replace an entity's AI with the ConfusedNPC AI for a [number_of_dice] turns.

    Parameters
    ----------
    kwargs:
       game_map (GameMap): Current game map.
       number_of_dice = kwargs.get('number_of_dice')
       target_x (int): x co-ordinate.
       target_y (int): y co-ordinate.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    game_map = kwargs.get('game_map')
    number_of_dice = kwargs.get('number_of_dice')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not game_map.current_level.fov[target_x, target_y]:
        results.append({ResultTypes.MESSAGE: Message('You cannot target a tile outside your field of view.', COLORS.get('neutral_text'))})
        return results

    entities = game_map.current_level.entities.get_entities_in_position((target_x, target_y))
    for entity in entities:
        if entity.ai:
            confused_ai = ConfusedNPC(entity.ai, number_of_dice)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({ResultTypes.MESSAGE: Message('The eyes of the {0} look vacant and they start to stumble around!'.format(entity.name), COLORS.get('effect_text'), target=entity, type=MessageType.EFFECT)})

            break
    else:
        results.append({ResultTypes.MESSAGE: Message('There is no targetable enemy at that location.', COLORS.get('neutral_text'))})

    return results

def fireball(**kwargs):
    '''Cast a fireball.

    Does FIRE damage to all damagable entities in a circle centered on the
    target point.

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       game_map (GameMap): Current game map.
       number_of_dice (int): number of die to roll.
       radius (int): radius of the spell effect.
       target_x (int): x co-ordinate.
       target_y (int): y co-ordinate.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    number_of_dice = kwargs.get('number_of_dice')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    type_of_dice = kwargs.get('type_of_dice')

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

def heal(**kwargs):
    '''Cast heal.

    Heal a target entity.

    Parameters
    ----------
    kwargs:
       number_of_dice (int): number of die to roll.
       target (Entity): The entity that is being targetted by the spell.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    number_of_dice = kwargs.get('number_of_dice')
    target = kwargs.get('target')
    type_of_dice = kwargs.get('type_of_dice')

    results = []

    if target.health.hp == target.health.max_hp:
        results.append({ResultTypes.MESSAGE: Message(f"{target.name} is already at full health.", COLORS.get('neutral_text'), target=target, type=MessageType.EFFECT)})
    else:
        target.health.heal(die_roll(number_of_dice, type_of_dice))
        results.append({ResultTypes.MESSAGE: Message(f"{target.name} wounds start to close up.", COLORS.get('success_text'), target=target, type=MessageType.EFFECT)})

    return results

def identify(**kwargs):
    '''Cast identify.

    If and entity has the Identifiable component and identifiable.identified is
    FALSE, switch to TRUE and print out a description of the entity.

    Parameters
    ----------
    kwargs:
       target (Entity): The entity that is being targetted by the spell.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    target = kwargs.get('target')

    results = []

    if target.identifiable and not target.identifiable.identified:
        target.identifiable.identified = True

    results.append({ResultTypes.MESSAGE: Message(f"The item is a {target.name}", COLORS.get('effect_text'))})
    if target.identifiable.common_ident:
        results.append({ResultTypes.COMMON_IDENT: target.base_name})

    return results

def lightning(**kwargs):
    '''Cast a lightning bolt.

    A bolt does ELECTRIC damage to all damagable entities in a line. The line is
    drawn between the caster, through the target point and stops when it hits a
    blocking tile.

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       game_map (GameMap): Current game map.
       number_of_dice (int): number of die to roll.
       target_x (int): x co-ordinate.
       target_y (int): y co-ordinate.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    number_of_dice = kwargs.get('number_of_dice')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    type_of_dice = kwargs.get('type_of_dice')

    ray = bresenham_ray(game_map, (caster.x, caster.y), (target_x, target_y))

    results = []

    ray.pop(0) #first item is caster xy

    for x,y in ray:
        entities = game_map.current_level.entities.get_entities_in_position((x,y))
        for entity in entities:
            if entity.health and not entity.health.dead:
                damage = die_roll(number_of_dice, type_of_dice)
                results.append({ResultTypes.MESSAGE: Message(f"A lighting bolt strikes the {entity.name} with a loud crack of thunder!", COLORS.get('effect_text'), target=entity, type=MessageType.EFFECT)})
                damage_results, total_damage = entity.health.take_damage(damage, caster, DamageType.ELECTRIC)
                results.append({ResultTypes.MESSAGE: Message(f"{entity.name} takes {str(total_damage)} damage.", COLORS.get('damage_text'))})
                results.extend(damage_results)

    return results

def magic_missile(**kwargs):
    '''Cast a number of magic missiles.

    Cast a missile that does 1d6 damage. 1 missile plus an additional missile
    per 3 caster level.
    e.g.:
    Caster level 1: 1 missile
    Caster level 3: 2 missiles
    Caster level 5: 2 missiles
    Caster level 7: 3 missiles
    etc.

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       game_map (GameMap): Current game map.
       target (Entity): The entity that is being targetted by the spell.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    target = kwargs.get('target')

    results = []

    if not game_map.current_level.fov[target.x, target.y]:
        results.append({ResultTypes.MESSAGE: Message('You cannot target a tile outside your field of view.', COLORS.get('neutral_text'))})
        return results
    else:
        end = bresenham_line(game_map, caster.point.tuple(), target.point.tuple())

        if end[-1] != target.point.tuple():
            results.append({ResultTypes.MESSAGE: Message('Target is not in line of sight.', COLORS.get('neutral_text'))})
            return results

    missiles = (caster.level.current_level // 3) + 1
    for _ in range(missiles):
        damage = die_roll(1, 6)
        results.append({ResultTypes.MESSAGE: Message(f"A magic missile strikes {target.name}.", COLORS.get('effect_text'), target=target, type=MessageType.EFFECT)})
        damage_results, total_damage = target.health.take_damage(damage, caster, DamageType.MAGIC)
        results.append({ResultTypes.MESSAGE: Message(f"{target.name} takes {str(total_damage)} damage.", COLORS.get('damage_text'))})
        results.extend(damage_results)

    return results

def mapping(**kwargs):
    '''Cast mapping.

    Reveal the entire game map.

    Parameters
    ----------
    kwargs:
       game_map (GameMap): Current game map.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    game_map = kwargs.get('game_map')

    results = []

    game_map.current_level.explored = np.full(game_map.current_level.grid.shape, 1, dtype=np.int8)

    results.append({ResultTypes.MESSAGE: Message('The scroll contains a map of immediate area.', COLORS.get('success_text'))})
    results.append({ResultTypes.FOV_RECOMPUTE: True})

    return results

def speed(**kwargs):
    '''Cast speed.

    Adjust an entities speed.

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       game_map (GameMap): Current game map.
       target (Entity): The entity that is being targetted by the spell.
       target_x (int): x co-ordinate.
       target_y (int): y co-ordinate.
       type_of_dice (int): Type of die to roll.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    target = kwargs.get('target')

    results = []

    if not target:
        if not game_map.current_level.fov[target_x, target_y]:
            results.append({ResultTypes.MESSAGE: Message('You cannot target a tile outside your field of view.', COLORS.get('neutral_text'))})
            return results

        entities = game_map.current_level.entities.get_entities_in_position((target_x, target_y))
        for entity in entities:
            if isinstance(entity, Character):
                target = entity
                break

    if target:
        target.add_component(Speed(), 'speed')
        target.speed.start()
        results.append({ResultTypes.MESSAGE: Message(f"{target.name} speeds up", COLORS.get('effect_text'), target=target, type=MessageType.EFFECT)})
    else:
        results.append({ResultTypes.MESSAGE: Message(f"Nothing to target", COLORS.get('effect_text'))})

    return results

def teleport(**kwargs):
    '''Cast teleport.

    Transport the casting entity to a random open tile on the map.
    There is a chance the teleport will have a secondary negative effect:
    10% of entity being damaged for 1d6 + distance between start and end points.
    1% chance a clone of the entity is created which hunts them down.

    Parameters
    ----------
    kwargs:
       caster (Entity): Entity that initiated the spell.
       game_map (GameMap): Current game map.

    Returns
    -------
    results (list)
        Results of casting the spell.
    '''
    caster = kwargs.get('caster')
    game_map = kwargs.get('game_map')

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

    elif (chance_of_teleport_going_wrong >= 89):
        damage_results, total_damage = caster.health.take_damage(die_roll(1, 6, int(orginal_point.distance_to(point))))
        results.append({ResultTypes.MESSAGE: Message(f"You take {str(total_damage)} damage.", COLORS.get('damage_text'))})
        results.extend(damage_results)

    return results
