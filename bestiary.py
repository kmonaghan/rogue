import libtcodpy as libtcod

import equipment
import game_state
import messageconsole
import quest

from components.ai import BasicNPC
from components.ai import StrollingNPC
from components.ai import WarlordNPC

from components.fighter import Fighter
from components.questgiver import Questgiver

from entities.character import Character

from map_objects.point import Point

def upgrade_npc(npc):
    npc.color = libtcod.silver
    npc.fighter.multiplier = 1.5
    npc.fighter.xp = npc.fighter.xp * 1.5
    item = equipment.random_magic_weapon()

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

def bountyhunter(point = None):
    #create a questgiver

    ai_component = StrollingNPC()
    npc = Character(point, '?', 'Bounty Hunter', libtcod.gold, blocks=True)
                     #blocks=True, fighter=None, ai=ai_component)

    questgiver = Questgiver()
    questgiver.owner = npc
    npc.questgiver = questgiver

    return npc

def goblin(point = None):
    #create a goblin
    fighter_component = Fighter(hp=10, defense=7, power=3, xp=10)
    ai_component = BasicNPC()

    npc = Character(point, 'G', 'goblin', libtcod.desaturated_green, blocks=True,
                    fighter=fighter_component, ai=ai_component)

    dagger = equipment.dagger()
    dagger.lootable = False

    npc.inventory.add_item(dagger)
    npc.equipment.toggle_equip(dagger)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def create_player():
    #create object representing the player
    fighter_component = Fighter(hp=100, defense=10, power=2, xp=0)

    player = Character(None, '@', 'player', libtcod.dark_green, blocks=True,
                       fighter=fighter_component)

    #initial equipment: a dagger
    dagger = equipment.dagger()
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    return player

def orc(point = None):
    #create an orc
    fighter_component = Fighter(hp=20, defense=10, power=4, xp=35)
    ai_component = BasicNPC()

    npc = Character(point, 'O', 'Orc', libtcod.light_green, blocks=True,
                    fighter=fighter_component, ai=ai_component)

    item = equipment.shortsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def troll(point = None):
    #create a troll
    fighter_component = Fighter(hp=30, defense=12, power=8, xp=100)
    ai_component = BasicNPC()

    npc = Character(point, 'T', 'troll', libtcod.darker_green, blocks=True,
                    fighter=fighter_component, ai=ai_component)

    item = equipment.longsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)

    return npc

def warlord(point = None):
    #create a warlord
    fighter_component = Fighter(hp=50, defense=10, power=4, xp=100)
    ai_component = WarlordNPC()

    npc = Character(point, 'W', 'Warlord', libtcod.black, blocks=True,
                    fighter=fighter_component, ai=ai_component)

    item = equipment.longsword()
    item.name = item.name + " of I'll FUCKING Have You"
    item.color = libtcod.purple
    item.equippable.power_bonus = item.equippable.power_bonus * 2
    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    shield = equipment.shield()
    shield.name = shield.name + " of Hide and Seek"
    shield.color = libtcod.purple
    shield.equipment.power_bonus = item.equippable.defense_bonus * 2
    npc.inventory.add_item(shield)
    npc.equipment.toggle_equip(shield)

    breastplate = equipment.breastplate()
    breastplate.name = breastplate.name + " of Rebounding"
    breastplate.color = libtcod.purple
    breastplate.equipment.power_bonus = item.equippable.defense_bonus * 2
    npc.inventory.add_item(breastplate)
    npc.equipment.toggle_equip(breastplate)

    return npc
