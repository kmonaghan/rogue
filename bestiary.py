import logging

import tcod

from random import choice, randint

import equipment

from game_messages import Message

import quest

from components.ai import (BasicNPC, CaptainNPC, CleanerNPC, GuardNPC,
                            PatrollingNPC, WarlordNPC, NecromancerNPC,
                            PredatorNPC, SpawningNPC, HatchingNPC,
                            TetheredNPC, ZombieNPC)
from components.berserk import Berserk
from components.children import Children
from components.damagemodifier import DamageModifier
from components.display import Display
from components.fov import FOV
from components.health import Health
from components.interaction import Interaction
from components.level import Level
from components.offence import Offence
from components.defence import Defence
from components.naming import Naming
from components.questgiver import Questgiver
from components.regeneration import Regeneration
from components.shimmer import Shimmer
from components.spawn import Spawn
from components.subspecies import Subspecies

from entities.entity import Entity
from entities.character import Character

from etc.colors import COLORS
from etc.configuration import CONFIG

from map_objects.point import Point

from components.death import PlayerDeath, WarlordDeath

from utils.random_utils import from_dungeon_level, random_choice_from_dict
from utils.utils import resource_path

from etc.enum import Interactions, MessageType, RenderOrder, Species, Tiles

import pubsub

names = False

creature_avoid = [Tiles.CORRIDOR_FLOOR, Tiles.DOOR, Tiles.ROOM_FLOOR, Tiles.STAIRS_FLOOR, Tiles.DEEP_WATER, Tiles.SHALLOW_WATER]
npc_avoid = [Tiles.DEEP_WATER]

'''
Create npc/creatures/player
'''

def bat(point = None, dungeon_level = 1):
    health_component = Health(4)

    creature = Character(point, 'B', 'bat', COLORS.get('bat'),
                    ai=PredatorNPC(species=Species.INSECT),
                    species=Species.BAT, health=health_component, act_energy=3)

    creature.add_component(Offence(base_power = 1), 'offence')
    creature.add_component(Defence(defence = 1), 'defence')
    creature.add_component(Level(xp_value = 10), 'level')

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    if randint(1, 100) >= 70:
        equipment.add_lifedrain(teeth)
        creature.add_component(Naming(creature.base_name, prefix='Vampiric'), 'naming')

    return creature

def batroost(point = None, dungeon_level = 1):
    health_component = Health(20)

    creature = Character(point, chr(225), 'Bat Roost', COLORS.get('bat_roost'),
                    ai=SpawningNPC(bat),
                    species=Species.BATROOST, health=health_component, act_energy=2)

    creature.add_component(Defence(defence = 5), 'defence')
    creature.add_component(Level(xp_value = 50), 'level')
    creature.add_component(Children(5), 'children')

    creature.movement.routing_avoid.extend(creature_avoid)

    equipment.add_random_loot(creature, dungeon_level)

    return creature

def bountyhunter(point):
    #create a questgiver

    ai_component = TetheredNPC(4, point)
    npc = Character(point, '?', 'Bounty Hunter', COLORS.get('bounty_hunter'),
                    ai=ai_component, interaction=Interactions.QUESTGIVER,
                    species=Species.NONDESCRIPT, act_energy=6)
    npc.add_component(Offence(base_power = 0), 'offence')
    npc.add_component(Defence(defence = 0), 'defence')
    npc.add_component(Questgiver(), 'questgiver')

    npc.movement.routing_avoid.extend(npc_avoid)

    return npc

def captain(point = None, dungeon_level = 1, upgrade_chance = 98, troops=5):
    npc = random_npc(point, dungeon_level, upgrade_chance)

    upgrade_npc(npc)

    if npc.species == Species.TROLL:
        underling = troll
    elif npc.species == Species.ORC:
        underling = orc
    elif npc.species == Species.GOBLIN:
        underling = goblin

    npc.add_component(CaptainNPC(underling), 'ai')
    npc.add_component(Children(troops), 'children')
    npc.add_component(Naming(npc.base_name, prefix='Captain'), 'naming')

    npc.movement.routing_avoid.extend(npc_avoid)

    return npc

def jailor(point = None, dungeon_level = 1, upgrade_chance = 98):
    npc = random_npc(point, dungeon_level, upgrade_chance)

    upgrade_npc(npc)

    npc.add_component(Naming(npc.base_name, prefix='Jailor'), 'naming')

    npc.movement.routing_avoid.extend(npc_avoid)

    return npc

def mimic(point = None, dungeon_level = 1):
    npc = Character(point, 'C', 'Chest', COLORS.get('mimic'), species=Species.CREATURE)

    npc.add_component(Health(30), 'health')
    npc.add_component(Offence(base_power = 3), 'offence')
    npc.add_component(Defence(defence = 3), 'defence')
    npc.add_component(Level(xp_value = 50), 'level')
    npc.add_component(Shimmer(alt_char = 'M', alt_chance = 95), 'shimmer')

    teeth = equipment.teeth()
    teeth.lootable = False

    npc.inventory.add_item(teeth)
    npc.equipment.toggle_equip(teeth)

    pubsub.pubsub.subscribe(pubsub.Subscription(npc, pubsub.PubSubTypes.ATTACKED, mimic_activate))

    return npc

def create_chest(point = None, dungeon_level = 1):
    npc = Character(point, 'C', 'Chest', COLORS.get('chest'), species=Species.NONDESCRIPT)

    if randint(1, 100) >= 95:
        return mimic(point, dungeon_level = 1)

    npc.add_component(Health(10), 'health')
    npc.add_component(Defence(defence = 2), 'defence')
    npc.add_component(Offence(base_power = 0), 'offence')
    #TODO: Generate random level appropriate loot in chest
    potion = equipment.random_potion(dungeon_level=dungeon_level)
    potion.lootable = True

    scroll = equipment.random_scroll(dungeon_level=dungeon_level)
    scroll.lootable = True

    weapon = equipment.random_magic_weapon(dungeon_level=dungeon_level)
    weapon.lootable = True

    armour = equipment.random_armour(dungeon_level=dungeon_level)
    armour.lootable = True

    npc.inventory.add_item(potion)
    npc.inventory.add_item(scroll)
    npc.inventory.add_item(weapon)
    npc.inventory.add_item(armour)

    return npc

def create_player():
    #create object representing the player
    health_component = Health(30)

    player = Character(None, '@', 'player', COLORS.get('player'),
                       death=PlayerDeath(), health=health_component,
                       species=Species.PLAYER, act_energy=4)

    player.add_component(Offence(base_power = 6), 'offence')
    player.add_component(Defence(defence = 6), 'defence')
    player.add_component(Level(), 'level')
    player.add_component(FOV(), 'fov')

    #initial equipment: a dagger
    dagger = equipment.create_weapon('dagger')

    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    armour = equipment.create_armour('leather')
    player.inventory.add_item(armour)
    player.equipment.toggle_equip(armour)

    if CONFIG.get('debug'):
        player.level.random_level_up(30)
        weapon = equipment.random_magic_weapon()
        player.inventory.add_item(weapon)
        player.equipment.toggle_equip(weapon)

        armour = equipment.random_armour()
        #equipment.add_damage_aura(armour)
        player.inventory.add_item(armour)
        player.equipment.toggle_equip(armour)

        ring = equipment.random_ring()
        player.inventory.add_item(ring)
        player.equipment.toggle_equip(ring)

        potion = equipment.healing_potion()
        player.inventory.add_item(potion)

        scroll1 = equipment.lighting_scroll()
        scroll1.identifiable.identified = True
        player.inventory.add_item(scroll1)

        scroll2 = equipment.fireball_scroll()
        scroll2.identifiable.identified = True
        player.inventory.add_item(scroll2)

        scroll3 = equipment.confusion_scroll()
        scroll3.identifiable.identified = True
        player.inventory.add_item(scroll3)

        scroll4 = equipment.identify_scroll()
        scroll4.identifiable.identified = True
        player.inventory.add_item(scroll4)

        scroll5 = equipment.speed_scroll()
        scroll5.identifiable.identified = True
        player.inventory.add_item(scroll5)

        scroll6 = equipment.teleport_scroll()
        scroll6.identifiable.identified = True
        player.inventory.add_item(scroll6)

        scroll7 = equipment.map_scroll()
        scroll7.identifiable.identified = True
        player.inventory.add_item(scroll7)

    pubsub.pubsub.subscribe(pubsub.Subscription(player, pubsub.PubSubTypes.EARNEDXP, earn_quest_xp))

    return player

def egg(point = None, dungeon_level = 1):
    health_component = Health(4)

    creature = Character(point, 'E', 'Snake Egg', COLORS.get('snake_egg'),
                    ai=HatchingNPC(snake),
                    species=Species.EGG, health=health_component)

    creature.movement.routing_avoid.extend(creature_avoid)

    creature.add_component(Offence(base_power = 1), 'offence')
    creature.add_component(Defence(defence = 1), 'defence')

    return creature

def gelatinous_cube(point = None, dungeon_level = 1):
    npc = Character(point, 'C', 'gelatinous cube', COLORS.get('gelatinous_cube'),
                    ai=CleanerNPC(), species=Species.OOZE,
                    render_order=RenderOrder.OVERLAY, health=Health(20))

    npc.add_component(Offence(base_power = 1), 'offence')
    npc.add_component(Defence(defence = 1), 'defence')
    npc.add_component(Level(xp_value = 10), 'level')

    cube_avoid = [Tiles.INTERNAL_DOOR, Tiles.EXIT_DOOR,
                    Tiles.DOOR, Tiles.CAVERN_FLOOR,
                    Tiles.FUNGAL_CAVERN_FLOOR,
                    Tiles.ROOM_FLOOR,
                    Tiles.SHALLOW_WATER, Tiles.DEEP_WATER,
                    Tiles.STAIRS_FLOOR, Tiles.SPAWN_POINT]

    npc.movement.routing_avoid.extend(cube_avoid)

    pseudopod = equipment.pseudopod()
    pseudopod.lootable = False
    equipment.add_paralysis(pseudopod)

    npc.inventory.add_item(pseudopod)
    npc.equipment.toggle_equip(pseudopod)

    return npc

def goblin(point = None, dungeon_level = 1):
    #create a goblin
    health_component = Health(20)
    ai_component = BasicNPC()

    npc = Character(point, 'G', 'goblin', COLORS.get('goblin'),
                    ai=ai_component, species=Species.GOBLIN,
                    health=health_component, act_energy=5)

    npc.add_component(Offence(base_power = 5), 'offence')
    npc.add_component(Defence(defence = 5), 'defence')
    npc.add_component(Level(xp_value = 10), 'level')

    npc.movement.routing_avoid.extend(npc_avoid)

    dagger = equipment.create_weapon('dagger')
    dagger.lootable = False

    npc.inventory.add_item(dagger)
    npc.equipment.toggle_equip(dagger)

    pubsub.pubsub.subscribe(pubsub.Subscription(npc, pubsub.PubSubTypes.DEATH, goblin_observed_death))

    return npc

def hornets(point = None, dungeon_level = 1):
    health_component = Health(2)

    creature = Character(point, chr(178), 'hornet', COLORS.get('hornet'),
                    ai=BasicNPC(),
                    species=Species.INSECT, health=health_component, act_energy=3)

    creature.add_component(Offence(base_power = 1), 'offence')
    creature.add_component(Defence(defence = 1), 'defence')
    creature.add_component(Level(xp_value = 10), 'level')
    creature.add_component(Display([chr(176),chr(176),chr(176),chr(177),chr(177),chr(177),chr(178),chr(178),chr(178)]), 'display')
    creature.add_component(DamageModifier(blunt=0.8, slashing=0.8, fire=1.2, ice=1.2, electric=1.2), 'damagemodifier')

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    return creature

def necromancer(point = None, dungeon_level = 1):
    #create a necromancer
    health_component = Health(30)
    ai_component = NecromancerNPC()

    npc = Character(point, 'N', 'necromancer', COLORS.get('necromancer'),
                    ai=ai_component, species=Species.NONDESCRIPT,
                    health=health_component)

    npc.add_component(Offence(base_power = 12), 'offence')
    npc.add_component(Defence(defence = 8), 'defence')
    npc.add_component(Level(xp_value = 10), 'level')
    npc.add_component(Children(6), 'children')

    npc.movement.routing_avoid.extend(npc_avoid)

    npc_level = (dungeon_level - 1) + randint(-1, 1)

    if npc_level > 1:
        npc.level.random_level_up(npc_level - 1)

    weapon = equipment.random_magic_weapon(dungeon_level=dungeon_level)
    weapon.lootable = True

    npc.inventory.add_item(weapon)
    npc.equipment.toggle_equip(weapon)

    num_of_potions = randint(0,3)

    for _ in range(num_of_potions):
        potion = equipment.random_potion(dungeon_level=dungeon_level)
        potion.lootable = True
        npc.inventory.add_item(potion)

    num_of_scrolls = randint(0,3)

    for _ in range(num_of_scrolls):
        scroll = equipment.random_scroll(dungeon_level=dungeon_level)
        scroll.lootable = True
        npc.inventory.add_item(scroll)

    return npc

def orc(point = None, dungeon_level = 1):
    #create an orc
    health_component = Health(20)
    ai_component = BasicNPC()

    npc = Character(point, 'O', 'orc', COLORS.get('orc'),
                    ai=ai_component, species=Species.ORC,
                    health=health_component, act_energy=5)

    npc.add_component(Offence(base_power = 10), 'offence')
    npc.add_component(Defence(defence = 4), 'defence')
    npc.add_component(Level(xp_value = 10), 'level')

    npc.movement.routing_avoid.extend(npc_avoid)

    item = equipment.create_weapon('shortsword')
    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def rat(point = None, dungeon_level = 1):
    health_component = Health(4)

    creature = Character(point, 'R', 'rat', COLORS.get('rat'),
                    ai=PredatorNPC(species=Species.EGG),
                    species=Species.RAT, health=health_component, act_energy=3)

    creature.add_component(Offence(base_power = 1), 'offence')
    creature.add_component(Defence(defence = 1), 'defence')
    creature.add_component(Level(xp_value = 10), 'level')

    creature.movement.routing_avoid.extend(creature_avoid)

    teeth = equipment.teeth()
    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    pubsub.pubsub.subscribe(pubsub.Subscription(creature, pubsub.PubSubTypes.ATTACKED, rat_swarm))

    return creature

def ratsnest(point = None, dungeon_level = 1):
    health_component = Health(20)

    creature = Character(point, 'N', 'rat\'s nest', COLORS.get('rats_nest'),
                    ai=SpawningNPC(rat),
                    species=Species.RATNEST, health=health_component, act_energy=2)

    creature.add_component(Defence(defence = 5), 'defence')
    creature.add_component(Level(xp_value = 50), 'level')
    creature.add_component(Children(5), 'children')

    creature.movement.routing_avoid.extend(creature_avoid)

    equipment.add_random_loot(creature, dungeon_level)

    return creature

def snake(point = None, dungeon_level = 1):
    health_component = Health(8)

    creature = Character(point, 'S', 'snake', COLORS.get('snake'),
                    ai=PredatorNPC(species=Species.RAT),
                    species=Species.SNAKE, health=health_component, act_energy=3)

    creature.add_component(Offence(base_power = 1), 'offence')
    creature.add_component(Defence(defence = 1), 'defence')
    creature.add_component(Level(xp_value = 10), 'level')
    creature.add_component(Spawn(2, egg), 'spawn')

    creature.movement.routing_avoid.extend(creature_avoid)

    teeth = equipment.teeth()

    if randint(1, 100) >= 50:
        equipment.add_poison(teeth, 1, 5)
        creature.add_component(Naming(creature.base_name, prefix='Poisonous'), 'naming')
        creature.color = COLORS.get('poisonous_snake')

    teeth.lootable = False

    creature.inventory.add_item(teeth)
    creature.equipment.toggle_equip(teeth)

    pubsub.pubsub.subscribe(pubsub.Subscription(creature, pubsub.PubSubTypes.DEATH, eat_rat))

    return creature

def troll(point = None, dungeon_level = 1):
    #create a troll
    health_component = Health(30)
    ai_component = BasicNPC()

    npc = Character(point, 'T', 'troll', COLORS.get('troll'),
                    ai=ai_component, species=Species.TROLL,
                    health=health_component, act_energy=6)

    npc.add_component(Offence(base_power = 12), 'offence')
    npc.add_component(Defence(defence = 8), 'defence')
    npc.add_component(Level(xp_value = 10), 'level')
    regen = Regeneration()
    npc.add_component(regen, 'regeneration')
    npc.add_component(DamageModifier(fire=1.5), 'damagemodifier')
    regen.start()

    npc.movement.routing_avoid.extend(npc_avoid)

    item = None
    dice = randint(1,100)
    if dice > 75:
        item = equipment.create_weapon('heavy mace')
        equipment.add_smashing(item)
    else:
        item = equipment.create_weapon('longsword')

    item.lootable = False

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    return npc

def warlord(point = None, dungeon_level = 1):
    #create a warlord
    ai_component = WarlordNPC()
    health_component = Health(50)

    npc = Character(point, 'W', 'Warlord', COLORS.get('warlord'),
                    ai=ai_component, species=Species.ORC, death=WarlordDeath(),
                    health=health_component)

    npc.add_component(Offence(base_power = 10), 'offence')
    npc.add_component(Defence(defence = 4), 'defence')
    npc.add_component(Level(xp_value = 10), 'level')

    npc.movement.routing_avoid.extend(npc_avoid)

    npc_level = (dungeon_level - 1) + randint(-1, 1)

    if npc_level > 1:
        npc.level.random_level_up(npc_level - 1)

    item = equipment.create_weapon('longsword')
    item.base_name = item.base_name + " of I'll FUCKING Have You"
    item.color = COLORS.get('equipment_epic')
    item.equippable.power = item.equippable.power * 2
    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

    shield = equipment.create_armour('steel shield')
    shield.base_name = shield.base_name + " of Hide and Seek"
    shield.color = COLORS.get('equipment_epic')
    shield.equippable.power = item.equippable.defence * 2
    npc.inventory.add_item(shield)
    npc.equipment.toggle_equip(shield)

    breastplate = equipment.create_armour('breastplate')
    breastplate.base_name = breastplate.base_name + " of Rebounding"
    breastplate.color = COLORS.get('equipment_epic')
    breastplate.equippable.power = item.equippable.defence * 2
    npc.inventory.add_item(breastplate)
    npc.equipment.toggle_equip(breastplate)

    return npc

'''
Helper methods to create npcs/creatures/objects
'''
def spawn_point(point = None, species = Species.GOBLIN, max_children=5):
    npc = Entity(point, ' ', '', COLORS.get('warlord'), blocks=False, invisible=True)

    if species == Species.TROLL:
        underling = troll
    elif species == Species.ORC:
        underling = orc
    elif species == Species.GOBLIN:
        underling = goblin

    npc.add_component(SpawningNPC(underling), 'ai')
    npc.add_component(Children(max_children), 'children')

    return npc

def generate_creature(type, dungeon_level = 1, point = None):
    creature = None

    if (type == Species.BAT):
        creature = bat(point, dungeon_level)
    elif (type == Species.BATROOST):
        creature = batroost(point, dungeon_level)
    elif (type == Species.RAT):
        creature = rat(point, dungeon_level)
    elif (type == Species.SNAKE):
        creature = snake(point, dungeon_level)
    elif (type == Species.RATNEST):
        creature = ratsnest(point, dungeon_level)
    elif (type == Species.EGG):
        creature = egg(point, dungeon_level)

    return creature

def random_npc(point = None, dungeon_level = 1, upgrade_chance = 98):
    npc_types = [Species.GOBLIN, Species.ORC, Species.TROLL]

    return generate_npc(choice(npc_types), dungeon_level, point, upgrade_chance)

def generate_npc(type, dungeon_level = 1, point = None, upgrade_chance = 98):
    global names

    if (type == Species.GOBLIN):
        npc = goblin(point)
    elif (type == Species.ORC):
        npc = orc(point)
    elif (type == Species.TROLL):
        npc = troll(point)

    if not names:
        tcod.namegen_parse(resource_path("data/names.txt"))
        names = True

    npc.base_name = tcod.namegen_generate(npc.base_name)

    npc_level = (dungeon_level - 1) + randint(-1, 1)

    if npc_level > 1:
        npc.level.random_level_up(npc_level - 1)

    dice = randint(1, 100)

    if (dice >= upgrade_chance):
        upgrade_npc(npc)
        npc.level.random_level_up(1)

    tweak_npc(npc)

    return npc

def reanmimate(npc):
    if (npc.death.skeletal):
        return convert_npc_to_skeleton(npc)

    return convert_npc_to_zombie(npc)

def generate_random_skeleton(point = None, dungeon_level = 1):
    npc = random_npc(point = point, dungeon_level = dungeon_level)

    return convert_npc_to_skeleton(npc)

def convert_npc_to_skeleton(npc):
    npc.char = 'S'
    npc.add_component(Naming(npc.base_name, prefix='Skeletal'), 'naming')
    npc.add_component(BasicNPC(), 'ai')
    npc.add_component(Health(max(1, npc.health.max_hp // 3)), 'health')
    npc.add_component(DamageModifier(blunt=1.2, slashing=0.8, poison=0), 'damagemodifier')

    npc.species=Species.UNDEAD
    npc.movement.routing_avoid.append(Tiles.SHALLOW_WATER)

    return npc

def generate_random_vampire(point = None, dungeon_level = 1):
    npc = random_npc(point = point, dungeon_level = dungeon_level)

    return convert_npc_to_vampire(npc)

def convert_npc_to_vampire(npc):
    npc.char = 'V'
    npc.add_component(Naming(npc.base_name, prefix='Vampiric'), 'naming')
    npc.add_component(Health(npc.health.max_hp * 1.5), 'health')
    npc.species=Species.UNDEAD
    npc.movement.routing_avoid.append(Tiles.SHALLOW_WATER)

    teeth = equipment.teeth()
    equipment.add_lifedrain(teeth)
    teeth.lootable = False

    npc.inventory.add_item(teeth)
    npc.equipment.toggle_equip(teeth)

    return npc

def generate_random_zombie(point = None, dungeon_level = 1):
    npc = random_npc(point = point, dungeon_level = dungeon_level)

    return convert_npc_to_zombie(npc)

def convert_npc_to_zombie(npc):
    npc.char = 'Z'
    npc.add_component(Naming(npc.base_name, prefix='Zombie'), 'naming')
    npc.add_component(ZombieNPC(species=npc.species), 'ai')
    npc.add_component(Health(max(1, npc.health.max_hp // 2)), 'health')
    npc.add_component(DamageModifier(blunt=0.8, slashing=1.2, poison=0), 'damagemodifier')
    npc.species=Species.UNDEAD
    npc.movement.routing_avoid.append(Tiles.SHALLOW_WATER)

    teeth = equipment.teeth()
    teeth.lootable = False
    equipment.add_infection(teeth, name="Zombification", chance=50,
                            on_turn=None, on_death=convert_npc_to_zombie)

    npc.inventory.add_item(teeth)
    npc.equipment.toggle_equip(teeth)

    return npc

def place_chest(point, level_map, player):
    chest = create_chest(point, level_map.dungeon_level)
    level_map.add_entity(chest)

    guards = randint(1, 3)

    npc_chances = {}
    npc_chances[Species.GOBLIN] = from_dungeon_level([[90, 1], [75, 2], [50, 3], [25, 4], [20, 5], [10, 6]], level_map.dungeon_level)
    npc_chances[Species.ORC] = from_dungeon_level([[9, 1], [20,2], [40, 3], [60, 4], [60, 5], [65, 6]], level_map.dungeon_level)
    npc_chances[Species.TROLL] = from_dungeon_level([[1, 1], [5,3], [10, 3], [15, 4], [20, 5], [25, 6]], level_map.dungeon_level)
    npc_choice = random_choice_from_dict(npc_chances)

    for _ in range(guards):
        npc = generate_npc(npc_choice, dungeon_level=level_map.dungeon_level, point=point)
        ai_component = GuardNPC(guard_point = chest.point)
        npc.add_component(ai_component, 'ai')
        ai_component.set_target(player)

        level_map.add_entity(npc)

def poison_npc(npc, dungeon_level = 1):
    weapon = equipment.random_weapon(dungeon_level = dungeon_level)
    damage = randint(dungeon_level, dungeon_level * 5)
    duration = randint(dungeon_level, dungeon_level * 10)
    equipment.add_poison(weapon, damage, duration)

    npc.inventory.add_item(weapon)
    npc.equipment.toggle_equip(weapon)

    return npc

def tweak_npc(npc):
    dice = randint(1, 100)
    if (dice < 50):
        return
    elif (dice < 55):
        poison_npc(npc)
    else:
        subspecies = Subspecies()
        subspecies.random_subspecies()
        npc.add_component(subspecies, 'subspecies')

def upgrade_npc(npc):
    npc.color = COLORS.get('elite')
    npc.offence.multiplier = 1.5
    npc.level.xp_value = npc.level.xp_value * 1.5
    item = equipment.random_magic_weapon()

    npc.inventory.add_item(item)
    npc.equipment.toggle_equip(item)

'''
Subscription methods
'''
def eat_rat(sub, message, level_map):
    if message.target is None:
        logging.info("eat_rat: the target is none?")
        return

    if sub.entity is None:
        logging.info("eat_rat: the subscriber is none?")
        return

    if (message.entity.species == Species.RAT) and (message.target.uuid == sub.entity.uuid):
        sub.entity.spawn.increase_energy()
        message.entity.death.skeletonize()

def goblin_observed_death(sub, message, level_map):
    if message.target is None:
        logging.info("goblin_observed_death: the target is none?")
        return

    if sub.entity is None:
        logging.info("goblin_observed_death: the subscriber is none?")
        return

    if ((message.entity.species == Species.GOBLIN) and (message.target.species == Species.PLAYER)):
        if (sub.entity.uuid == message.entity.uuid):
            pass
        elif level_map.current_level.fov[sub.entity.x, sub.entity.y]:
            if not sub.entity.berserk:
                sub.entity.add_component(Berserk(), 'berserk')
                sub.entity.berserk.start()
                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message(f"{sub.entity.name.title()} has gone berserk!", COLORS.get('effect_text'), source=sub.entity, type=MessageType.EFFECT)))

def mimic_activate(sub, message, level_map):
    if (sub.entity.uuid == message.target.uuid):
        sub.entity.add_component(BasicNPC(), 'ai')
        sub.entity.char = 'M'
        sub.entity.base_name = 'Mimic'
        sub.entity.del_component('shimmer')
        sub.entity.ai.set_target(message.entity)
        pubsub.pubsub.mark_subscription_for_removal(sub)

def mimic_shimmer(sub, message, level_map):
    if sub.entity.ai:
        pubsub.pubsub.mark_subscription_for_removal(sub)
        return

    if (sub.entity.char == 'M'):
        sub.entity.char = 'C'
        sub.entity.base_name = 'Chest'
    else:
        mimic_chance = randint(1, 100)
        if (mimic_chance >= 99):
            sub.entity.char = 'M'
            sub.entity.base_name = 'Mimic'

def rat_swarm(sub, message, level_map):
    if (message.entity.species == Species.PLAYER) and (message.target.species == Species.RATNEST):
        if level_map.current_level.fov[sub.entity.x, sub.entity.y]:
            if sub.entity.ai:
                sub.entity.ai.set_target(message.entity)

def earn_quest_xp(sub, message, level_map):
    if (message.target.uuid == sub.entity.uuid):
        xp = message.entity.xp
        sub.entity.level.add_xp(xp)
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message(f"{sub.entity.name} gained {xp} experience points.", target=sub.entity, type=MessageType.EVENT)))
