import json
import logging

from random import randint, choice

import tcod

import tome

from etc.colors import COLORS
from utils.random_utils import from_dungeon_level, random_choice_from_dict
from utils.utils import resource_path

from components.ablity import (Defence, ExtraDamage, Poisoning, PushBack,
                                LifeDrain, Infection, Paralysis, Speed,
                                SpellAbility)
from components.aura import DamageAura
from components.equippable import Equippable
from components.identifiable import (Identifiable, IdentifiablePotion,
                                        IdentifiableScroll, IdentifiableWeapon)
from components.item import Item
from components.naming import Naming
from components.regeneration import Regeneration
from components.usable import ScrollUsable, PotionUsable
from components.unlock import Unlock

from entities.entity import Entity

from game_messages import Message

from etc.enum import (DamageType,
                        EquipmentSlot,
                        Interactions,
                        RenderOrder,
                        string_to_damage_type,
                        string_to_equipment_slot,)

from utils.utils import resource_path

identified_items = {}
potion_descriptions = {}
potion_random_details = False

armours = {}
weapons = {}

def random_armour(point = None, dungeon_level = 1):
    data = choice(list(armours.values()))
    return armour_from_json(data, point = point)

def random_potion(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['heal'] = 40
    item_chances['offence'] = 40
    item_chances['defence'] = 40
    item_chances['antidote'] = 40
    item_chances['speed'] = 40

    choice = random_choice_from_dict(item_chances)
    if choice == 'heal':
        item = healing_potion(point)
    elif choice == 'offence':
            item = power_potion(point)
    elif choice == 'defence':
        item = defence_potion(point)
    elif choice == 'antidote':
        item = antidote_potion(point)
    elif choice == 'speed':
        item = speed_potion(point)

    return item

def random_ring(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['power'] = 50
    item_chances['defence'] = 50
    item_chances['regeneration'] = 5

    item = Entity(point, chr(9), 'Ring', COLORS.get('equipment_rare'), render_order=RenderOrder.ITEM)

    choice = random_choice_from_dict(item_chances)
    if choice == 'power':
        add_power(item)
    elif choice == 'defence':
        add_defence(item)
    elif choice == 'regeneration':
        add_regeneration(item)
    return item

def random_scroll(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['lightning'] = 40
    item_chances['fireball'] = 30
    item_chances['confuse'] = 30
    item_chances['map_scroll'] = 20
    item_chances['identify'] = 20
    item_chances['teleport'] = 20
    item_chances['speed'] = 20

    choice = random_choice_from_dict(item_chances)
    if choice == 'lightning':
        item = lighting_scroll(point)

    elif choice == 'fireball':
        item = fireball_scroll(point)

    elif choice == 'confuse':
        item = confusion_scroll(point)

    elif choice == 'map_scroll':
        item = map_scroll(point)

    elif choice == 'identify':
        item = identify_scroll(point)

    elif choice == 'teleport':
        item = teleport_scroll(point)

    elif choice == 'speed':
        item = speed_scroll(point)

    return item

def random_weapon(point = None, dungeon_level = 1):
    data = choice(list(weapons.values()))
    return weapon_from_json(data, point = point)

def create_armour(name, point = None, dungeon_level = 1):
    armour = armours.get(name)

    if armour:
        return armour_from_json(armour, point = point)

    return None

def create_weapon(name, point = None, dungeon_level = 1):
    weapon = weapons.get(name)

    if weapon:
        return weapon_from_json(weapon, point = point)

    logging.info(f"No loaded weapon called {name}")

    return None


def random_magic_weapon(dungeon_level = 1):
    item = random_weapon(dungeon_level = dungeon_level)

    dice = randint(1, 1000)

    item.add_component(IdentifiableWeapon(item.base_name),"identifiable")

    naming = Naming(item.base_name)

    if (dice <= 500):
        naming.prefix = "Remarkable"
        item.color = COLORS.get('equipment_uncommon')
        item.equippable.number_of_dice = 2
    elif (dice <= 750):
        naming.prefix = "Excellent"
        item.color = COLORS.get('equipment_rare')
        item.equippable.number_of_dice = 3
    elif (dice <= 990):
        naming.prefix = "Exceptional"
        item.color = COLORS.get('equipment_epic')
        item.equippable.number_of_dice = 4
    else:
        naming.prefix = "Phenomenal"
        item.color = COLORS.get('equipment_legendary')
        item.equippable.number_of_dice = 5
    item.add_component(naming, 'naming')

    '''
    naming.suffix = "of Stabby Stabby"
    naming.suffix = "of YORE MA"
    naming.suffix = "of I'll FUCKING Have You"
    naming.suffix = "of Des and Troy"
    '''

    add_random_weapon_ablity(item)

    return item

def add_random_weapon_ablity(item):
    dice = randint(1, 100)

    if dice <=50:
        return

    if not item.identifiable:
        item.add_component(IdentifiableWeapon(item.base_name),"identifiable")

    if dice <= 50:
        add_poison(item, 1, 10)
    elif dice <= 60:
        add_flaming(item)
    elif dice <= 70:
        add_shocking(item)
    elif dice <= 80:
        add_smashing(item)
    elif dice <= 90:
        add_lifedrain(item)
    elif dice <= 95:
        add_defence(item)
    elif dice <= 95:
        add_defence(item)
    elif dice <= 95:
        add_defence(item)

def add_defence(item):
    item.add_component(Defence(defence=10), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of defence'), 'naming')

def add_poison(item, damage = 1, duration = 10):
    item.add_component(Poisoning(0, damage, duration), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of poisoning'), 'naming')

def add_flaming(item):
    item.add_component(ExtraDamage(number_of_dice=1, type_of_dice=6, name="fire", damage_type=DamageType.FIRE), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, prefix = 'Flaming'), 'naming')
    else:
        item.naming.prefix += " flaming"

def add_lightning(item):
    item.add_component(SpellAbility(spell=tome.lightning, number_of_dice=2, type_of_dice=10, radius=2), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of lightning'), 'naming')
    else:
        item.naming.prefix += " shocking"

def add_shocking(item):
    item.add_component(ExtraDamage(number_of_dice=1, type_of_dice=6, name="shock", damage_type=DamageType.ELECTRIC), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of shocking'), 'naming')

def add_smashing(item):
    item.add_component(PushBack(), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of smashing'), 'naming')

def add_lifedrain(item):
    item.add_component(LifeDrain(), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of life drain'), 'naming')

def add_paralysis(item):
    item.add_component(Paralysis(), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of paralysis'), 'naming')

def add_power(item):
    item.add_component(Defence(defence=1), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of power'), 'naming')

def add_regeneration(item):
    item.add_component(Defence(defence=10), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of regeneration'), 'naming')

def add_speed(item):
    item.add_component(Speed(), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = 'of speed'), 'naming')

def add_infection(item, name="Infection", chance=50, on_turn=None, on_death=None):
    item.add_component(Infection(name=name, chance=chance, on_turn=on_turn, on_death=on_death), 'ablity')
    if not item.naming:
        item.add_component(Naming(item.base_name, suffix = f"of {name}"), 'naming')

def ring_of_regeneration(point = None):
    equippable_component = Equippable(EquipmentSlot.RING, attribute=Regeneration())
    item = Entity(point, chr(9), 'Ring of Regeneration', COLORS.get('equipment_rare'), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
    return item

def create_potion(point, usable):
    item = Entity(point, chr(173), usable.name, COLORS.get('equipment_uncommon'),
                    render_order=RenderOrder.ITEM, item=Item(), usable=usable)

    return potion_description(item)

def potion_description(item):
    global potion_random_details

    description = potion_descriptions.get(item.base_name)
    if not description:
        if not potion_random_details:
            tcod.namegen_parse(resource_path("data/liquids.txt"))
            potion_random_details = True
        description = {}
        description['container'] = tcod.namegen_generate('potion_container')
        description['liquid_color'] = tcod.namegen_generate('potion_colours')
        description['liquid_type'] = tcod.namegen_generate('potion_texture')
        potion_descriptions[item.base_name] = description

    item.add_component(IdentifiablePotion(container=description['container'],
                                            liquid_color=description['liquid_color'],
                                            liquid_type=description['liquid_type']),
                                            "identifiable")

    return item

def antidote_potion(point = None):
    usable = PotionUsable(name="Antidote", spell=tome.antidote)

    return create_potion(point, usable)

def healing_potion(point = None, number_of_dice=1, type_of_dice=8):
    usable = PotionUsable(name="Healing Potion", spell=tome.heal, number_of_dice=number_of_dice, type_of_dice=type_of_dice)

    return create_potion(point, usable)

def power_potion(point = None, number_of_dice=1, type_of_dice=8):
    usable = PotionUsable(name="Power Potion", spell=tome.change_power, number_of_dice=number_of_dice, type_of_dice=type_of_dice)

    return create_potion(point, usable)

def defence_potion(point = None, number_of_dice=1, type_of_dice=8):
    usable = PotionUsable(name="Defence Potion", spell=tome.change_defence, number_of_dice=number_of_dice, type_of_dice=type_of_dice)

    return create_potion(point, usable)

def speed_potion(point = None):
    usable = PotionUsable(name="Speed Potion", spell=tome.speed)

    return create_potion(point, usable)

def lighting_scroll(point = None):
    #create a lightning bolt scroll
    usable = ScrollUsable(scroll_name="Lightning Scroll",
                            scroll_spell=tome.lightning,
                            number_of_dice=3,
                            type_of_dice=10,
                            radius=2,
                            targets_inventory=False)

    item = Entity(point, '#', 'Lightning Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                                  item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")
    return item

def fireball_scroll(point = None):
    #create a fireball scroll
    usable = ScrollUsable(scroll_name="Fireball Scroll",
                            scroll_spell=tome.fireball,
                            number_of_dice=3,
                            type_of_dice=6,
                            radius=3,
                            targets_inventory=False)
    usable.needs_target = True
    usable.targeting_message = Message('Left-click a target tile for the fireball, or right-click to cancel.', COLORS.get('instruction_text'))

    item = Entity(point, '#', 'Fireball Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                                  item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")

    return item

def confusion_scroll(point = None):
    #create a confuse scroll
    usable = ScrollUsable(scroll_name="Confusion Scroll",
                            scroll_spell=tome.confuse,
                            targets_inventory=False)
    usable.needs_target = True
    usable.targeting_message = Message('Left-click a target NPC for the confusion spell, or right-click to cancel.', COLORS.get('instruction_text'))

    item = Entity(point, '#', 'Confusion Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                                  item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")

    return item

def identify_scroll(point = None):
    usable = ScrollUsable(scroll_name="Identify Scroll", scroll_spell=tome.identify, targets_inventory=True)

    item = Entity(point, '#', usable.name, COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")

    return item

def speed_scroll(point = None):
    usable = ScrollUsable(scroll_name="Speed Scroll", scroll_spell=tome.speed, targets_inventory=False)
    usable.needs_target = True
    usable.targeting_message = Message('Left-click a target NPC for the speed spell, or right-click to cancel.', COLORS.get('instruction_text'))

    item = Entity(point, '#', usable.name, COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")

    return item

def teleport_scroll(point = None):
    usable = ScrollUsable(scroll_name="Teleport Scroll", scroll_spell=tome.teleport, targets_inventory=False)

    item = Entity(point, '#', usable.name, COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")

    return item

def map_scroll(point = None):
    usable = ScrollUsable(scroll_name="Mapping Scroll", scroll_spell=tome.mapping)

    item = Entity(point, '#', usable.name, COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

    item.add_component(IdentifiableScroll(), "identifiable")

    return item

def teeth(point = None):
    #create teeth for animals
    equippable_component = Equippable(EquipmentSlot.MAIN_HAND, power=1)
    equippable_component.type_of_dice = 2
    equippable_component.damage_type = DamageType.SLASHING
    item = Entity(point, '"', 'teeth', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def claw(point = None):
    #create claw for animals
    equippable_component = Equippable(EquipmentSlot.MAIN_HAND, power=1)
    equippable_component.type_of_dice = 4
    equippable_component.damage_type = DamageType.SLASHING
    item = Entity(point, ',', 'claw', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def pseudopod(point = None):
    equippable_component = Equippable(EquipmentSlot.MAIN_HAND, power=1)
    equippable_component.type_of_dice = 6
    equippable_component.damage_type = DamageType.BLUNT
    item = Entity(point, ',', 'pseudopod', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def key(point = None, unlocks = None):
    key = Entity(point, 'k', 'key', COLORS.get('light_door'),
                    blocks=False, interaction=Interactions.NONE,
                    render_order=RenderOrder.ITEM, item=Item())
    key.add_component(Unlock(unlocks.uuid), 'unlock')

    return key

def add_damage_aura(item):
    item.add_component(DamageAura(), 'aura')

def add_random_loot(npc, dungeon_level = 1, min_items = 0):
    total_items = randint(min_items, min_items + dungeon_level)

    for i in range(total_items):
        pick = randint(0,4)
        if pick == 0:
            item = random_armour(dungeon_level = dungeon_level)
        elif pick == 1:
            item = random_potion(dungeon_level = dungeon_level)
        elif pick == 2:
            item = random_ring(dungeon_level = dungeon_level)
        elif pick == 3:
            item = random_scroll(dungeon_level = dungeon_level)
        elif pick == 4:
            item = random_magic_weapon(dungeon_level = dungeon_level)

        item.lootable = True
        npc.inventory.add_item(item)

def weapon_from_json(data, point = None):
    slot = string_to_damage_type.get(data['Equipment Slots'], EquipmentSlot.MAIN_HAND)

    equippable_component = Equippable(slot, power=data['Power'])
    equippable_component.damage_type = string_to_damage_type.get(data['Damage']['Damage Type'], DamageType.DEFAULT)
    equippable_component.number_of_dice = data['Damage']['number_of_dice']
    equippable_component.type_of_dice = data['Damage']['type_of_dice']

    item = Entity(point,
                    data['Character'],
                    data['Name'],
                    COLORS.get('equipment_common'),
                    equippable=equippable_component,
                    render_order=RenderOrder.ITEM)

    return item

def armour_from_json(data, point = None):
    slot = string_to_equipment_slot.get(data['Equipment Slot'], EquipmentSlot.CHEST)

    equippable_component = Equippable(slot, defence=data['Defence'])

    item = Entity(point,
                    data['Character'],
                    data['Name'],
                    COLORS.get('equipment_common'),
                    equippable=equippable_component,
                    render_order=RenderOrder.ITEM)

    return item

def import_armour():
    with open(resource_path('data/equipment/armour.json')) as json_file:
        data = json.load(json_file)

        for detail in data:
            armours[detail["Name"]] = detail

def import_weapons():
    with open(resource_path('data/equipment/weapons.json')) as json_file:
        data = json.load(json_file)

        for detail in data:
            weapons[detail["Name"]] = detail

def fingfangfoom(item):
    if item.equippable.slot == EquipmentSlot.HEAD:
        name = "gloom"
    elif item.equippable.slot == EquipmentSlot.CHEST:
        name = "doom"
    elif item.equippable.slot == EquipmentSlot.LEGS:
        name = "doom"
    elif item.equippable.slot == EquipmentSlot.FEET:
        add_speed(item)
        name = "zoom"
    elif item.equippable.slot == EquipmentSlot.MAIN_HAND:
        name = "kaboom"
        add_smashing(item)
    else:
        return

    item.naming.prefix = "Fing Fang Foom"
    item.suffix = f"of {name}"
