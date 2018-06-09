import libtcodpy as libtcod
import baseclasses
import characterclass
import messageconsole
import ai
import equipment
import quest
import pc

from map_objects.point import Point

def upgrade_npc(npc):
    npc.color = libtcod.silver
    npc.fighter.multiplier = 1.5
    npc.fighter.xp = npc.fighter.xp * 1.5
    item = equipment.random_magic_weapon()
    npc.add_to_inventory(item)
    item.equipment.equip()

def bountyhunter(point = None):
    #create a questgiver

    ai_component = ai.StrollingNPC()
    npc = baseclasses.Character(point, '?', 'Bounty Hunter', libtcod.gold,
                     blocks=True, fighter=None, ai=ai_component)

    questgiver = characterclass.Questgiver()
    questgiver.owner = npc
    npc.questgiver = questgiver

    return npc

def goblin(point = None):
    #create a goblin
    fighter_component = characterclass.Fighter(hp=10, defense=7, power=3, xp=10, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(point, 'G', 'goblin', libtcod.desaturated_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    dice = libtcod.random_get_int(0, 1, 100)

    item = equipment.dagger()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def orc(point = None):
    #create an orc
    fighter_component = characterclass.Fighter(hp=20, defense=10, power=4, xp=35, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(point, 'O', 'Orc', libtcod.light_green,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    item = equipment.shortsword()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def troll(point = None):
    #create a troll
    fighter_component = characterclass.Fighter(hp=30, defense=12, power=8, xp=100, death_function=npc_death)
    ai_component = ai.BasicNPC()

    npc = baseclasses.Character(point, 'T', 'troll', libtcod.darker_green,
                     blocks=True, fighter=fighter_component, ai=ai_component)

    item = equipment.longsword()
    item.lootable = False

    npc.add_to_inventory(item)
    item.equipment.equip()

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def warlord(point = None):
    #create a warlord
    fighter_component = characterclass.Fighter(hp=50, defense=10, power=4, xp=100, death_function=warlord_death)
    ai_component = ai.WarlordNPC()

    npc = baseclasses.Character(point, 'W', 'Warlord', libtcod.black,
                                    blocks=True, fighter=fighter_component, ai=ai_component)

    item = equipment.longsword()
    item.name = item.name + " of I'll FUCKING Have You"
    item.color = libtcod.purple
    item.equipment.power_bonus = item.equipment.power_bonus * 2
    npc.add_to_inventory(item)
    item.equipment.equip()

    shield = equipment.shield()
    shield.name = shield.name + " of Hide and Seek"
    shield.color = libtcod.purple
    shield.equipment.power_bonus = item.equipment.defense_bonus * 2
    npc.add_to_inventory(shield)
    shield.equipment.equip()

    breastplate = equipment.breastplate()
    breastplate.name = breastplate.name + " of Rebounding"
    breastplate.color = libtcod.purple
    breastplate.equipment.power_bonus = item.equipment.defense_bonus * 2
    npc.add_to_inventory(breastplate)
    breastplate.equipment.equip()

    return npc

def npc_death(npc):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    messageconsole.message('The ' + npc.name + ' is dead! You gain ' + str(npc.fighter.xp) + ' experience points.', libtcod.orange)

    quest.check_quests_for_npc_death(npc)

    npc.char = '%'
    npc.color = libtcod.dark_red
    npc.blocks = False
    npc.fighter = None
    npc.ai = None
    npc.name = 'remains of ' + npc.name
    npc.send_to_back()

    for item in npc.inventory:
        if (item.lootable):
            item.item.drop()

def warlord_death(npc):
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
            item.item.drop()
