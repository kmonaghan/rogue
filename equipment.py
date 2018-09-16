import libtcodpy as libtcod

import random_utils
import tome

from components.equippable import Equippable
from components.item import Item

from entities.entity import Entity

from game_messages import Message

from tome import cast_confuse, cast_fireball, cast_lightning, heal, cast_mapping

from equipment_slots import EquipmentSlots
from render_order import RenderOrder

def random_armour(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['shield'] = random_utils.from_dungeon_level([[40, 1], [20, 2], [15, 3]], dungeon_level)
    item_chances['helmet'] = random_utils.from_dungeon_level([[30, 2], [15, 3], [10, 4]], dungeon_level)
    item_chances['leather shirt'] = random_utils.from_dungeon_level([[40, 1], [20, 2], [15, 3]], dungeon_level)
    item_chances['scalemail'] = random_utils.from_dungeon_level([[10, 1], [40, 2], [30, 3], [15, 4]], dungeon_level)
    item_chances['chainmail'] = random_utils.from_dungeon_level([[40, 3], [30, 4]], dungeon_level)
    item_chances['breastplate'] = random_utils.from_dungeon_level([[15, 4]], dungeon_level)

    choice = random_utils.random_choice_from_dict(item_chances)
    if choice == 'shield':
        item = shield(point)

    elif choice == 'helmet':
        item = helmet(point)

    elif choice == 'leather shirt':
        item = leathershirt(point)

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

    choice = random_utils.random_choice_from_dict(item_chances)
    if choice == 'heal':
        item = healing_potion(point)

    return item

def random_scroll(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['lightning'] = 40
    item_chances['fireball'] = 30
    item_chances['confuse'] = 30
    item_chances['map_scroll'] = 20

    choice = random_utils.random_choice_from_dict(item_chances)
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
    item_chances['dagger'] = random_utils.from_dungeon_level([[60, 1], [40, 2], [20, 3], [10, 4]], dungeon_level)
    item_chances['short sword'] = random_utils.from_dungeon_level([[30, 1], [40, 2], [45, 3], [40, 4]], dungeon_level)
    item_chances['long sword'] = random_utils.from_dungeon_level([[10, 1], [20, 2], [35, 3], [40, 4], [60, 5]], dungeon_level)

    choice = random_utils.random_choice_from_dict(item_chances)
    if choice == 'dagger':
        item = dagger(point)

    elif choice == 'short sword':
        item = shortsword(point)

    elif choice == 'long sword':
        item = longsword(point)

    return item

def random_magic_weapon(dungeon_level = 1):
    item = random_weapon(None, dungeon_level)

    dice = libtcod.random_get_int(0, 1, 1000)

    if (dice <= 500):
        item.name = item.name + " of Stabby Stabby"
        item.color = libtcod.chartreuse
        item.equippable.power_bonus = item.equippable.power_bonus * 1.25
    elif (dice <= 750):
        item.name = item.name + " of YORE MA"
        item.color = libtcod.blue
        item.equippable.power_bonus = item.equippable.power_bonus * 1.5
    elif (dice <= 990):
        item.name = item.name + " of I'll FUCKING Have You"
        item.color = libtcod.purple
        item.equippable.power_bonus = item.equippable.power_bonus * 2
    else:
        item.name = item.name + " of Des and Troy"
        item.color = libtcod.crimson
        item.equippable.power_bonus = item.equippable.power_bonus * 4

    item.equippable.number_of_dice = 2

    return item

def healing_potion(point = None):
    item_component = Item(use_function=heal, number_of_dice=1, type_of_dice=8)

    item = Entity(point, '!', 'Healing Potion', libtcod.violet, render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def lighting_scroll(point = None):
    #create a lightning bolt scroll
    item_component = Item(use_function=cast_lightning, number_of_dice=2, type_of_dice=10, maximum_range=5)
    item = Entity(point, '#', 'Lightning Scroll', libtcod.yellow, render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def fireball_scroll(point = None):
    #create a fireball scroll
    item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                          number_of_dice=3, type_of_dice=6, radius=3)
    item = Entity(point, '#', 'Fireball Scroll', libtcod.light_yellow, render_order=RenderOrder.ITEM,
                                  item=item_component)

    return item

def confusion_scroll(point = None):
    #create a confuse scroll
    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan))
    item = Entity(point, '#', 'Confusion Scroll', libtcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def map_scroll(point = None):
    item_component = Item(use_function=cast_mapping)
    item = Entity(point, '#', 'Mapping Scroll', libtcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def shield(point = None):
    #create a shield
    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
    item = Entity(point, '[', 'shield', libtcod.darker_orange, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def helmet(point = None):
    #create a helmet
    equippable_component = Equippable(EquipmentSlots.HEAD, defense_bonus=1)
    item = Entity(point, '^', 'helmet', libtcod.darker_orange, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def leathershirt(point = None):
    #create a chainmail
    equippable_component = Equippable(EquipmentSlots.CHEST, defense_bonus=1)
    item = Entity(point, '=', 'leather shirt', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def scalemail(point = None):
    #create a chainmail
    equippable_component = Equippable(EquipmentSlots.CHEST, defense_bonus=2)
    item = Entity(point, '=', 'scalemail', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def chainmail(point = None):
    #create a chainmail
    equippable_component = Equippable(EquipmentSlots.CHEST, defense_bonus=3)
    item = Entity(point, '=', 'chainmail', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def breastplate(point = None):
    #create a breastplate
    equippable_component = Equippable(EquipmentSlots.CHEST, defense_bonus=4)
    item = Entity(point, '=', 'breastplate', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def dagger(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    equippable_component.type_of_dice = 4
    item = Entity(point, '-', 'dagger', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def shortsword(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
    equippable_component.type_of_dice = 6
    item = Entity(point, '/', 'short sword', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def longsword(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=4)
    equippable_component.type_of_dice = 8
    item = Entity(point, '\\', 'long sword', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def teeth(point = None):
    #create teeth for animals
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    equippable_component.type_of_dice = 2
    item = Entity(point, '"', 'teeth', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def claw(point = None):
    #create claw for animals
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    equippable_component.type_of_dice = 4
    item = Entity(point, ',', 'claw', libtcod.sky, equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item
