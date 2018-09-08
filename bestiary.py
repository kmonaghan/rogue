import libtcodpy as libtcod

import equipment
import game_state
import quest

from components.ai import BasicNPC
from components.ai import StrollingNPC
from components.ai import WarlordNPC
from components.ai import NecromancerNPC
from components.ai import Hunter
from components.ai import Hatching

from components.fighter import Fighter
from components.questgiver import Questgiver

from entities.character import Character

from map_objects.point import Point

from components.death import PlayerDeath, WarlordDeath

from species import Species

def upgrade_npc(npc):
    npc.color = libtcod.silver
    npc.fighter.multiplier = 1.5
    npc.fighter.xp = npc.fighter.xp * 1.5
    item = equipment.random_magic_weapon()

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

def bountyhunter(point = None):
    #create a questgiver

    ai_component = StrollingNPC(tethered = point)
    npc = Character(point, '?', 'Bounty Hunter', libtcod.gold,  ai=ai_component, species=Species.NONDESCRIPT)

    questgiver = Questgiver()
    questgiver.owner = npc
    npc.questgiver = questgiver

    return npc

def goblin(point = None):
    #create a goblin
    fighter_component = Fighter(hp=20, defense=5, power=5, xp=10)
    ai_component = BasicNPC()

    npc = Character(point, 'G', 'goblin', libtcod.desaturated_green,
                    fighter=fighter_component, ai=ai_component, species=Species.GOBLIN)

    dagger = equipment.dagger()
    dagger.lootable = False

    npc.inventory.add_item(dagger)
    npc.equipment.toggle_equip(dagger)

    return npc

def create_player():
    #create object representing the player
    fighter_component = Fighter(hp=30, defense=6, power=6, xp=0)

    if (game_state.debug == True):
        fighter_component.hp = 1000
        fighter_component.base_defense = 200
        fighter_component.base_power = 200

    player = Character(None, '@', 'player', libtcod.dark_green,
                       fighter=fighter_component, death=PlayerDeath())

    #initial equipment: a dagger
    dagger = equipment.dagger()
    if (game_state.debug == True):
        dagger.number_of_dice = 100

    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    return player

def orc(point = None):
    #create an orc
    fighter_component = Fighter(hp=20, defense=10, power=4, xp=35)
    ai_component = BasicNPC()

    npc = Character(point, 'O', 'orc', libtcod.light_green,
                    fighter=fighter_component, ai=ai_component, species=Species.ORC)

    item = equipment.shortsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def troll(point = None):
    #create a troll
    fighter_component = Fighter(hp=30, defense=12, power=8, xp=100)
    ai_component = BasicNPC()

    npc = Character(point, 'T', 'troll', libtcod.darker_green,
                    fighter=fighter_component, ai=ai_component, species=Species.TROLL)

    item = equipment.longsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def warlord(point = None):
    #create a warlord
    fighter_component = Fighter(hp=50, defense=10, power=4, xp=100)
    ai_component = WarlordNPC()

    npc = Character(point, 'W', 'Warlord', libtcod.black,
                    fighter=fighter_component, ai=ai_component, species=Species.ORC, death=WarlordDeath())

    item = equipment.longsword()
    item.name = item.name + " of I'll FUCKING Have You"
    item.color = libtcod.purple
    item.equippable.power_bonus = item.equippable.power_bonus * 2
    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    shield = equipment.shield()
    shield.name = shield.name + " of Hide and Seek"
    shield.color = libtcod.purple
    shield.equippable.power_bonus = item.equippable.defense_bonus * 2
    npc.inventory.add_item(shield)
    npc.equipment.toggle_equip(shield)

    breastplate = equipment.breastplate()
    breastplate.name = breastplate.name + " of Rebounding"
    breastplate.color = libtcod.purple
    breastplate.equippable.power_bonus = item.equippable.defense_bonus * 2
    npc.inventory.add_item(breastplate)
    npc.equipment.toggle_equip(breastplate)

    return npc

def skeleton(point = None, old_npc = None):
    fighter_component = Fighter(hp=30, defense=12, power=8, xp=100)
    ai_component = BasicNPC()

    npc = Character(point, 'S', 'skeleton', libtcod.darker_green,
                    fighter=fighter_component, ai=ai_component, species=Species.NONDESCRIPT)

    if old_npc:
        npc.species = old_npc.species
        npc.x = old_npc.x
        npc.y = old_npc.y
        npc.name = 'Skeletal ' + old_npc.name

    item = equipment.longsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def necromancer(point = None):
    #create a necromancer
    fighter_component = Fighter(hp=30, defense=12, power=8, xp=100)
    ai_component = NecromancerNPC()

    npc = Character(point, 'N', 'necromancer', libtcod.darker_green,
                    fighter=fighter_component, ai=ai_component, species=Species.NONDESCRIPT)

    item = equipment.longsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

#    dice = libtcod.random_get_int(0, 1, 100)

#    if (dice >= 98):
#        upgrade_npc(npc)

    return npc

names = False

def generate_npc(type, dungeon_level = 1, player_level = 1, point = None):
    global names

    if (type == Species.GOBLIN):
        npc = goblin(point)
    elif (type == Species.ORC):
        npc = orc(point)
    elif (type == Species.TROLL):
        npc = troll(point)

    if not names:
        libtcod.namegen_parse('data/names.txt')
        names = True

    npc.name = libtcod.namegen_generate(npc.name)

    npc_level = (dungeon_level - 1) + player_level + libtcod.random_get_int(0, -1, 1)

    if npc_level > 1:
        npc.level.random_level_up(npc_level - 1)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= 98):
        upgrade_npc(npc)
        npc.level.random_level_up(1)

    print("final npc level: " + str(npc.level.current_level))
    return npc
