import libtcodpy as libtcod

import equipment
from game_states import debug
import quest

from entities.chest import Chest

from components.ai import BasicNPC
from components.ai import StrollingNPC
from components.ai import WarlordNPC
from components.ai import NecromancerNPC
from components.ai import Hunter
from components.ai import Hatching
from components.ai import SpawnNPC

from components.fighter import Fighter
from components.health import Health
from components.offense import Offense
from components.defence import Defence
from components.questgiver import Questgiver
from components.subspecies import Subspecies

from entities.character import Character

from map_objects.point import Point

from components.death import PlayerDeath, WarlordDeath

from random_utils import from_dungeon_level, random_choice_from_dict

from species import Species

def upgrade_npc(npc):
    npc.color = libtcod.silver
    npc.offense.multiplier = 1.5
    npc.level.xp_value = npc.level.xp_value * 1.5
    item = equipment.random_magic_weapon()

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

def tweak_npc(npc):
    dice = libtcod.random_get_int(0, 1, 100)
    if (dice < 50):
        return
    else:
        subspecies = Subspecies()
        subspecies.random_subspecies()
        npc.add_component(subspecies, "subspecies")

def bountyhunter(point = None):
    #create a questgiver

    ai_component = StrollingNPC(tethered = point)
    npc = Character(point, '?', 'Bounty Hunter', libtcod.gold, ai=ai_component, species=Species.NONDESCRIPT)

    questgiver = Questgiver()
    questgiver.owner = npc
    npc.questgiver = questgiver

    return npc

def create_player():
    #create object representing the player
    health_component = Health(30)

    player = Character(None, '@', 'player', libtcod.dark_green,
                       death=PlayerDeath(), health=health_component)

    player.add_component(Offense(base_power = 6), "offense")
    player.add_component(Defence(defence = 6), "defence")

    #initial equipment: a dagger
    dagger = equipment.dagger()

    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    if debug:
        player.level.random_level_up(20)
        weapon = equipment.random_magic_weapon()
        player.inventory.add_item(weapon)
        player.equipment.toggle_equip(weapon)

    return player

def bat(point = None):
    fighter_component = Fighter(xp=2)
    health_component = Health(4)

    creature = Character(point, 'B', 'bat', libtcod.darker_red,
                    ai=StrollingNPC(attacked_ai=BasicNPC()),
                    species=Species.BAT, health=health_component)

    creature.add_component(Offense(base_power = 1), "offense")
    creature.add_component(Defence(defence = 1), "defence")

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    return creature

def egg(point = None):
    fighter_component = Fighter(xp=0)
    health_component = Health(4)

    creature = Character(point, 'E', 'Snake Egg', libtcod.darker_gray,
                    ai=Hatching(snake()),
                    species=Species.EGG, health=health_component)

    creature.add_component(Offense(base_power = 1), "offense")
    creature.add_component(Defence(defence = 1), "defence")

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    return creature

def goblin(point = None):
    #create a goblin
    fighter_component = Fighter(xp=10)
    health_component = Health(20)
    ai_component = BasicNPC()

    npc = Character(point, 'G', 'goblin', libtcod.desaturated_green,
                    ai=ai_component, species=Species.GOBLIN,
                    health=health_component)

    npc.add_component(Offense(base_power = 5), "offense")
    npc.add_component(Defence(defence = 5), "defence")

    dagger = equipment.dagger()
    dagger.lootable = False

    npc.inventory.add_item(dagger)
    npc.equipment.toggle_equip(dagger)

    return npc

def necromancer(point = None):
    #create a necromancer
    fighter_component = Fighter(xp=100)
    health_component = Health(30)
    ai_component = NecromancerNPC()

    npc = Character(point, 'N', 'necromancer', libtcod.darker_green,
                    ai=ai_component, species=Species.NONDESCRIPT,
                    health=health_component)

    npc.add_component(Offense(base_power = 12), "offense")
    npc.add_component(Defence(defence = 8), "defense")

    item = equipment.longsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def orc(point = None):
    #create an orc
    fighter_component = Fighter(xp=35)
    health_component = Health(20)
    ai_component = BasicNPC()

    npc = Character(point, 'O', 'orc', libtcod.light_green,
                    ai=ai_component, species=Species.ORC,
                    health=health_component)

    npc.add_component(Offense(base_power = 10), "offense")
    npc.add_component(Defence(defence = 4), "defence")

    item = equipment.shortsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def rat(point = None):
    fighter_component = Fighter(xp=2)
    health_component = Health(4)

    creature = Character(point, 'R', 'rat', libtcod.darker_green,
                    ai=Hunter(attacked_ai=BasicNPC(), hunting=Species.EGG),
                    species=Species.RAT, health=health_component)

    creature.add_component(Offense(base_power = 1), "offense")
    creature.add_component(Defence(defence = 1), "defence")

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    return creature

def ratsnest(point = None):
    fighter_component = Fighter(xp=2)
    health_component = Health(4)

    creature = Character(point, 'N', 'rat\'s nest', libtcod.darker_green,
                    ai=SpawnNPC(rat),
                    species=Species.RAT, health=health_component)

    creature.add_component(Defence(defence = 4), "defence")

    # potion = equipment.random_potion(dungeon_level = dungeon_level)
    # potion.lootable = True
    #
    # creature.inventory.add_item(potion)

    return creature

def reanmimate(old_npc):
    if (old_npc.death.skeletal):
        return skeleton(old_npc.point, old_npc)

    return zombie(old_npc.point, old_npc)

def skeleton(point = None, old_npc = None):
    ai_component = BasicNPC()
    fighter_component = Fighter(xp=100)
    health_component = Health(30)

    if old_npc:
        old_npc.blocks = True
        old_npc.char = 'S'
        old_npc.base_name = 'Skeletal ' + old_npc.base_name
        old_npc.add_component(ai_component, "ai")
        old_npc.add_component(Health(old_npc.health.max_hp // 4), "health")

        return old_npc
    else:
        npc = Character(point, 'S', 'skeleton', libtcod.darker_green,
                        ai=ai_component, species=Species.NONDESCRIPT,
                        health=health_component)

        npc.add_component(Offense(base_power = 12), "offense")
        npc.add_component(Defence(defence = 8), "defence")

        item = equipment.longsword()
        item.lootable = False

        npc.inventory.add_item(item)
        npc.equipment.toggle_equip(item)

    return npc

def snake(point = None):
    fighter_component = Fighter(xp=4)
    health_component = Health(8)

    creature = Character(point, 'S', 'snake', libtcod.darker_green,
                    ai=Hunter(attacked_ai=BasicNPC(), hunting=Species.RAT),
                    species=Species.SNAKE, health=health_component)

    creature.add_component(Offense(base_power = 1), "offense")
    creature.add_component(Defence(defence = 1), "defence")

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    return creature

def troll(point = None):
    #create a troll
    fighter_component = Fighter(xp=100)
    health_component = Health(30)
    ai_component = BasicNPC()

    npc = Character(point, 'T', 'troll', libtcod.darker_green,
                    ai=ai_component, species=Species.TROLL,
                    health=health_component)

    npc.add_component(Offense(base_power = 12), "offense")
    npc.add_component(Defence(defence = 8), "defense")

    item = equipment.longsword()
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def warlord(point = None):
    #create a warlord
    fighter_component = Fighter(xp=100)
    ai_component = WarlordNPC()

    npc = Character(point, 'W', 'Warlord', libtcod.black,
                    ai=ai_component, species=Species.ORC, death=WarlordDeath(),
                    health=health_component)

    npc.add_component(Offense(base_power = 10), "offense")
    npc.add_component(Defence(defence = 4), "defense")

    item = equipment.longsword()
    item.base_name = item.base_name + " of I'll FUCKING Have You"
    item.color = libtcod.purple
    item.equippable.power_bonus = item.equippable.power_bonus * 2
    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    shield = equipment.shield()
    shield.base_name = shield.base_name + " of Hide and Seek"
    shield.color = libtcod.purple
    shield.equippable.power_bonus = item.equippable.defence_bonus * 2
    npc.inventory.add_item(shield)
    npc.equipment.toggle_equip(shield)

    breastplate = equipment.breastplate()
    breastplate.base_name = breastplate.base_name + " of Rebounding"
    breastplate.color = libtcod.purple
    breastplate.equippable.power_bonus = item.equippable.defence_bonus * 2
    npc.inventory.add_item(breastplate)
    npc.equipment.toggle_equip(breastplate)

    return npc

def zombie(point = None, old_npc = None):
    ai_component = BasicNPC()
    fighter_component = Fighter(xp=100)
    health_component = Health(30)

    if old_npc:
        old_npc.blocks = True
        old_npc.char = 'Z'
        old_npc.base_name = 'Zombie ' + old_npc.base_name
        old_npc.add_component(ai_component, "ai")
        old_npc.add_component(Health(old_npc.health.max_hp // 2), "health")
        old_npc.add_component(fighter_component, "fighter")

        return old_npc
    else:
        npc = Character(point, 'Z', 'zombie', libtcod.darker_green,
                        fighter=fighter_component, ai=ai_component,
                        species=Species.NONDESCRIPT, health=health_component)

        npc.add_component(Offense(base_power = 10), "offense")
        npc.add_component(Defence(defence = 4), "defense")

        item = equipment.longsword()
        item.lootable = False

        npc.inventory.add_item(item)
        npc.equipment.toggle_equip(item)

    return npc

names = False

def generate_creature(type, dungeon_level = 1, player_level = 1, point = None):
    creature = None

    if (type == Species.BAT):
        creature = bat(point)
    elif (type == Species.RAT):
        creature = rat(point)
    elif (type == Species.SNAKE):
        creature = snake(point)
    elif (type == Species.RATNEST):
        creature = ratsnest(point)
    elif (type == Species.EGG):
        creature = egg(point)

    return creature

def generate_npc(type, dungeon_level = 1, player_level = 1, point = None, upgrade_chance = 98):
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

    npc.base_name = libtcod.namegen_generate(npc.base_name)

    npc_level = (dungeon_level - 1) + libtcod.random_get_int(0, -1, 1)

    if npc_level > 1:
        npc.level.random_level_up(npc_level - 1)

    dice = libtcod.random_get_int(0, 1, 100)

    if (dice >= upgrade_chance):
        upgrade_npc(npc)
        npc.level.random_level_up(1)

    print("final npc level: " + str(npc.level.current_level))

    tweak_npc(npc)

    return npc

def place_chest(point, game_map):
    chest = Chest(point, game_map.dungeon_level)
    game_map.add_entity_to_map(chest)

    guards = libtcod.random_get_int(0, 1, 3)

    npc_chances = {}
    npc_chances[Species.GOBLIN] = from_dungeon_level([[90, 1], [75, 2], [50, 3], [25, 4], [20, 5], [10, 6]], game_map.dungeon_level)
    npc_chances[Species.ORC] = from_dungeon_level([[9, 1], [20,2], [40, 3], [60, 4], [60, 5], [65, 6]], game_map.dungeon_level)
    npc_chances[Species.TROLL] = from_dungeon_level([[1, 1], [5,3], [10, 3], [15, 4], [20, 5], [25, 6]], game_map.dungeon_level)
    npc_choice = random_choice_from_dict(npc_chances)

    for i in range(guards):
        npc = generate_npc(npc_choice, dungeon_level=game_map.dungeon_level, point=point)
        ai_component = StrollingNPC(tethered = point, tethered_distance = 2, aggressive = True)
        ai_component.attacked_ai = npc.ai
        npc.add_component(ai_component, "ai")

        game_map.add_entity_to_map(npc)
