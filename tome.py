import libtcodpy as libtcod
import messageconsole
import pc
import bestiary
import baseclasses

#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

def cast_heal():
    #heal the player
    if pc.player.fighter.hp == pc.player.fighter.max_hp:
        messageconsole.message('You are already at full health.', libtcod.red)
        return 'cancelled'

    messageconsole.message('Your wounds start to feel better!', libtcod.light_violet)
    pc.player.fighter.heal(HEAL_AMOUNT)

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

    for obj in baseclasses.objects:  #damage every fighter in range, including the player
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

def cast_summon_goblin(pc):
    dice = libtcod.random_get_int(0, 1, 6)

    npcs = []
    for idx in range(0, dice):
        npc = bestiary.goblin()
        npcs.append(npc)

    start_x = pc.x - 1
    start_y = pc.y - 1

    for offset in range(0, 2):
        if (baseclasses.is_blocked(start_x + offset, start_y + offset) == False):
            npc = npcs.pop(0)
            baseclasses.objects.append(npc)

        if len(npcs) == 0:
            return

    start_x = pc.x

    for offset in range(0, 2):
        if (baseclasses.is_blocked(start_x + offset, start_y + offset) == False):
            npc = npcs.pop(0)
            baseclasses.objects.append(npc)

        if len(npcs) == 0:
            return

    start_x = pc.x + 1

    for offset in range(0, 2):
        if (baseclasses.is_blocked(start_x + offset, start_y + offset) == False):
            npc = npcs.pop(0)
            baseclasses.objects.append(npc)

        if len(npcs) == 0:
            return
