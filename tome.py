import libtcodpy as libtcod

from components.ai import ConfusedNPC

from map_objects.point import Point

from game_messages import Message

from random_utils import die_roll

#spell values
HEAL_AMOUNT = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3

def heal(*args, **kwargs):
    entity = args[0]
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    target = kwargs.get('target')

    results = []

    if entity.health.hp == entity.health.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', libtcod.yellow)})
    else:
        entity.health.heal(die_roll(number_of_dice, type_of_dice))
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', libtcod.green)})

    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.point.distance_to(entity.point)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        damage = die_roll(number_of_dice, type_of_dice)
        results.append({'consumed': True, 'target': target, 'message': Message('A lighting bolt strikes the {0} with a loud thunder! The damage is {1}'.format(target.name, damage))})
        results.extend(target.health.take_damage(damage, caster))
    else:
        results.append({'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike.', libtcod.red)})

    return results


def cast_fireball(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    number_of_dice = kwargs.get('number_of_dice')
    type_of_dice = kwargs.get('type_of_dice')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    results.append({'consumed': True, 'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius), libtcod.orange)})

    for entity in entities:
        if entity.point.distance_to(Point(target_x, target_y)) <= radius and entity.fighter:
            damage = die_roll(number_of_dice, type_of_dice)
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage), libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage, caster))

    return results


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedNPC(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True, 'message': Message('The eyes of the {0} look vacant, as he starts to stumble around!'.format(entity.name), libtcod.light_green)})

            break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_summon_npc(point, ncp_type, game_map, number_of_npc=6):
    dice = libtcod.random_get_int(0, 1, number_of_npc)

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
            if not game_map.is_blocked(Point(x, y)):
                npc = ncp_type(Point(x, y))
                game_map.add_entity_to_map(npc)
                dice -= 1

                if dice < 1:
                    return

def resurrect_all_npc(npc_type, game_map, target):
    for entity in game_map.entities:
        if entity.health and entity.health.dead:
            npc_type(entity)
    return

def cast_mapping(*args, **kwargs):
    game_map = kwargs.get('game_map')

    results = []

    for y in range(game_map.height):
        for x in range(game_map.width):
            game_map.map[x][y].explored = True

    results.append({'consumed': True, 'fov_recompute': True, 'message': Message('The scroll contains a map of immediate area.', libtcod.gold)})

    return results
