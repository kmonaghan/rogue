import libtcodpy as libtcod
import baseclasses
import characterclass
import messageconsole
import ai
import equipment

def upgrade_npc(npc):
    npc.color = libtcod.silver
    npc.fighter.multiplier = 1.5
    npc.fighter.xp = npc.fighter.xp * 1.5
    item = equipment.random_magic_weapon()
    npc.add_to_inventory(item)

def goblin(x, y):
    #create a goblin
    fighter_component = characterclass.Fighter(hp=10, defense=7, power=3, xp=10, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(x, y, 'G', 'goblin', libtcod.desaturated_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    item = equipment.dagger()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def orc(x, y):
    #create an orc
    fighter_component = characterclass.Fighter(hp=20, defense=10, power=4, xp=35, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(x, y, 'O', 'Orc', libtcod.light_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    item = equipment.shortsword()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def troll(x, y):
    #create a troll
    fighter_component = characterclass.Fighter(hp=30, defense=12, power=8, xp=100, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(x, y, 'T', 'troll', libtcod.darker_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    item = equipment.longsword()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def orc(x, y):
    #create an orc
    fighter_component = characterclass.Fighter(hp=20, defense=10, power=4, xp=35, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(x, y, 'O', 'Orc', libtcod.light_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    item = equipment.shortsword()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc
    
def npc_death(npc):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    messageconsole.message('The ' + npc.name + ' is dead! You gain ' + str(npc.fighter.xp) + ' experience points.', libtcod.orange)
    npc.char = '%'
    npc.color = libtcod.dark_red
    npc.blocks = False
    npc.fighter = None
    npc.ai = None
    npc.name = 'remains of ' + npc.name
    npc.send_to_back()

    for item in npc.inventory:
        if (item.lootable):
            item.x = npc.x
            item.y = npc.y
            baseclasses.objects.append(item)
