import libtcodpy as libtcod
import messageconsole
import bestiary
import baseclasses
import screenrendering

import components.ai

from map_objects.map_utils import is_blocked
from map_objects.point import Point

import game_state

#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

def closest_npc(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in game_state.objects:
        if object.fighter and not object == game_state.player and libtcod.map_is_in_fov(baseclasses.fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = game_state.player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, screenrendering.key, screenrendering.mouse)
        screenrendering.render_all()

        (x, y) = (screenrendering.mouse.cx, screenrendering.mouse.cy)

        #x_offset = (gamemap.MAX_MAP_WIDTH - gamemap.MAP_WIDTH)/ 2
        #y_offset = (gamemap.MAX_MAP_HEIGHT - gamemap.MAP_HEIGHT) / 2

        #x -= x_offset
        #y -= y_offset

        if screenrendering.mouse.rbutton_pressed or screenrendering.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (screenrendering.mouse.lbutton_pressed and libtcod.map_is_in_fov(baseclasses.fov_map, x, y) and
                (max_range is None or game_state.player.distance(x, y) <= max_range)):
            return (x, y)

def target_npc(max_range=None):
    #returns a clicked npc inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked npc, otherwise continue looping
        for obj in game_state.objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != game_state.player:
                return obj

def cast_heal():
    #heal the player
    if game_state.player.fighter.hp == game_state.player.fighter.max_hp:
        messageconsole.message('You are already at full health.', libtcod.red)
        return 'cancelled'

    messageconsole.message('Your wounds start to feel better!', libtcod.light_violet)
    game_state.player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    npc = closest_npc(LIGHTNING_RANGE)
    if npc is None:  #no enemy found within maximum range
        messageconsole.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    #zap it!
    messageconsole.message('A lighting bolt strikes the ' + npc.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
    npc.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    messageconsole.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    messageconsole.message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

    for obj in game_state.objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            messageconsole.message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)

def cast_confuse():
    #ask the player for a target to confuse
    messageconsole.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    npc = target_npc(CONFUSE_RANGE)
    if npc is None: return 'cancelled'

    #replace the npc's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = npc.ai
    npc.ai = ConfusedNPC(old_ai)
    npc.ai.owner = npc  #tell the new component who owns it
    messageconsole.message('The eyes of the ' + npc.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_summon_npc(point, ncp_type, number_of_npc=6):
    dice = libtcod.random_get_int(0, 1, number_of_creatures)

    print "Will generate " + str(dice) + " NPCs"

    start_x = point.x - 1
    start_y = point.y - 1

    for offset in range(0, 3):
        if (is_blocked(Point(start_x, start_y + offset)) == False):
            npc = ncp_type(start_x, start_y + offset)
            game_state.objects.append(npc)
            dice -= 1

            if dice < 1:
                return

    start_x = point.x

    for offset in range(0, 3):
        if (is_blocked(Point(start_x, start_y + offset)) == False):
            npc = ncp_type(start_x, start_y + offset)
            game_state.objects.append(npc)
            dice -=1

            if dice < 1:
                return

    start_x = pc.x + 1

    for offset in range(0, 3):
        if (is_blocked(Point(start_x, start_y + offset)) == False):
            npc = ncp_type(start_x, start_y + offset)
            game_state.objects.append(npc)
            dice -= 1

            if dice < 1:
                return
