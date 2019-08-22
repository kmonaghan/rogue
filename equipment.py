from random import randint

import tcod

from etc.colors import COLORS
from utils.random_utils import from_dungeon_level, random_choice_from_dict
import tome

from components.equippable import Equippable
from components.item import Item
from components.usable import HealingPotionUsable, ScrollUsable

from entities.entity import Entity

from game_messages import Message

from tome import cast_confuse, cast_fireball, cast_lightning, heal, cast_mapping

from equipment_slots import EquipmentSlots
from etc.enum import RenderOrder

def random_armour(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['shield'] = from_dungeon_level([[40, 1], [20, 2], [15, 3]], dungeon_level)
    item_chances['helmet'] = from_dungeon_level([[30, 2], [15, 3], [10, 4]], dungeon_level)
    item_chances['leather shirt'] = from_dungeon_level([[40, 1], [20, 2], [15, 3]], dungeon_level)
    item_chances['splint armour'] = from_dungeon_level([[40, 2], [20, 3], [15, 4]], dungeon_level)
    item_chances['scalemail'] = from_dungeon_level([[10, 1], [40, 2], [30, 3], [15, 4]], dungeon_level)
    item_chances['chainmail'] = from_dungeon_level([[40, 3], [30, 4]], dungeon_level)
    item_chances['breastplate'] = from_dungeon_level([[15, 4]], dungeon_level)

    choice = random_choice_from_dict(item_chances)
    if choice == 'shield':
        item = shield(point)

    elif choice == 'helmet':
        item = helmet(point)

    elif choice == 'leather shirt':
        item = leathershirt(point)

    elif choice == 'splint armour':
        item = splint(point)

    elif choice == 'scalemail':
        item = scalemail(point)

    elif choice == 'chainmail':
        item = chainmail(point)

    elif choice == 'breastplate':
        item = breastplate(point)

    return item

def random_potion(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['heal'] = 40

    choice = random_choice_from_dict(item_chances)
    if choice == 'heal':
        item = healing_potion(point)

    return item

def random_ring(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['power'] = 50
    item_chances['defence'] = 50

    choice = random_choice_from_dict(item_chances)
    if choice == 'power':
        item = ring_of_power(point)

    elif choice == 'defence':
        item = ring_of_defence(point)

    return item

def random_scroll(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['lightning'] = 40
    item_chances['fireball'] = 30
    item_chances['confuse'] = 30
    item_chances['map_scroll'] = 20

    choice = random_choice_from_dict(item_chances)
    if choice == 'lightning':
        item = lighting_scroll(point)

    elif choice == 'fireball':
        item = fireball_scroll(point)

    elif choice == 'confuse':
        item = confusion_scroll(point)

    elif choice == 'map_scroll':
        item = map_scroll(point)

    return item

def random_weapon(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['dagger'] = from_dungeon_level([[60, 1], [40, 2], [20, 3], [10, 4]], dungeon_level)
    item_chances['short sword'] = from_dungeon_level([[30, 1], [40, 2], [45, 3], [40, 4]], dungeon_level)
    item_chances['long sword'] = from_dungeon_level([[10, 1], [20, 2], [35, 3], [40, 4], [60, 5]], dungeon_level)
    item_chances['axe'] = from_dungeon_level([[10, 1], [20, 2], [35, 3], [40, 4], [60, 5]], dungeon_level)
    item_chances['mace'] = from_dungeon_level([[10, 1], [20, 2], [35, 3], [40, 4], [60, 5]], dungeon_level)

    choice = random_choice_from_dict(item_chances)
    if choice == 'dagger':
        item = dagger(point)

    elif choice == 'short sword':
        item = shortsword(point)

    elif choice == 'long sword':
        item = longsword(point)

    elif choice == 'axe':
        item = axe(point)

    elif choice == 'mace':
        item = mace(point)

    return item

def random_magic_weapon(dungeon_level = 1):
    item = random_weapon(None, dungeon_level)

    dice = randint(1, 1000)

    if (dice <= 500):
        item.base_name = item.base_name + " of Stabby Stabby"
        item.color = COLORS.get('equipment_uncommon')
        item.equippable.power_bonus = item.equippable.power_bonus * 1.25
    elif (dice <= 750):
        item.base_name = item.base_name + " of YORE MA"
        item.color = COLORS.get('equipment_rare')
        item.equippable.power_bonus = item.equippable.power_bonus * 1.5
    elif (dice <= 990):
        item.base_name = item.base_name + " of I'll FUCKING Have You"
        item.color = COLORS.get('equipment_epic')
        item.equippable.power_bonus = item.equippable.power_bonus * 2
    else:
        item.base_name = item.base_name + " of Des and Troy"
        item.color = COLORS.get('equipment_legendary')
        item.equippable.power_bonus = item.equippable.power_bonus * 4

    item.equippable.number_of_dice = 2

    return item

def ring_of_power(point = None):
    equippable_component = Equippable(EquipmentSlots.RING, power_bonus=1)
    item = Entity(point, 'o', 'Ring of Power', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
    return item

def ring_of_defence(point = None):
    equippable_component = Equippable(EquipmentSlots.RING, defence_bonus=1)
    item = Entity(point, 'o', 'Ring of Health', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
    return item

def healing_potion(point = None):
    item = Entity(point, '!', 'Healing Potion', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=HealingPotionUsable())

    return item

def lighting_scroll(point = None):
    #create a lightning bolt scroll
    item_component = Item(use_function=cast_lightning, number_of_dice=2, type_of_dice=10, maximum_range=5)
    item = Entity(point, '#', 'Lightning Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def fireball_scroll(point = None):
    #create a fireball scroll
    item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan),
                                          number_of_dice=3, type_of_dice=6, radius=3)
    item = Entity(point, '#', 'Fireball Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                                  item=item_component)

    return item

def confusion_scroll(point = None):
    #create a confuse scroll
    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan))
    item = Entity(point, '#', 'Confusion Scroll', tcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def map_scroll(point = None):
    usable = ScrollUsable(scroll_name="Mapping Scroll", scroll_spell=cast_mapping)

    item = Entity(point, '#', usable.name, tcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

    return item

def shield(point = None):
    #create a shield
    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defence_bonus=1)
    item = Entity(point, '[', 'shield', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def helmet(point = None):
    #create a helmet
    equippable_component = Equippable(EquipmentSlots.HEAD, defence_bonus=1)
    item = Entity(point, '^', 'helmet', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def leathershirt(point = None):
    #create a chainmail
    equippable_component = Equippable(EquipmentSlots.CHEST, defence_bonus=1)
    item = Entity(point, '=', 'leather shirt', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def splint(point = None):
    #create a breastplate
    equippable_component = Equippable(EquipmentSlots.CHEST, defence_bonus=2)
    item = Entity(point, '=', 'splint armour', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def scalemail(point = None):
    #create a chainmail
    equippable_component = Equippable(EquipmentSlots.CHEST, defence_bonus=3)
    item = Entity(point, '=', 'scalemail', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def chainmail(point = None):
    #create a chainmail
    equippable_component = Equippable(EquipmentSlots.CHEST, defence_bonus=4)
    item = Entity(point, '=', 'chainmail', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def breastplate(point = None):
    #create a breastplate
    equippable_component = Equippable(EquipmentSlots.CHEST, defence_bonus=5)
    item = Entity(point, '=', 'breastplate', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def axe(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    equippable_component.type_of_dice = 8
    item = Entity(point, '-', 'axe', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def dagger(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    equippable_component.type_of_dice = 4
    item = Entity(point, '-', 'dagger', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def shortsword(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
    equippable_component.type_of_dice = 6
    item = Entity(point, '/', 'short sword', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def longsword(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=4)
    equippable_component.type_of_dice = 8
    item = Entity(point, '\\', 'long sword', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def mace(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    equippable_component.type_of_dice = 10
    item = Entity(point, '-', 'mace', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def teeth(point = None):
    #create teeth for animals
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    equippable_component.type_of_dice = 2
    item = Entity(point, '"', 'teeth', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def claw(point = None):
    #create claw for animals
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    equippable_component.type_of_dice = 4
    item = Entity(point, ',', 'claw', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item
