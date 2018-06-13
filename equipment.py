import libtcodpy as libtcod
import messageconsole
import baseclasses
import tome

import game_state

from components.equipment import Equipment
from components.item import Item

from entities.object import Object

from equipment_slots import EquipmentSlots

def random_armour(point = None):
    item_chances = {}
    item_chances['shield'] = baseclasses.from_dungeon_level([[40, 1], [20, 2], [15, 3]])
    item_chances['helmet'] = baseclasses.from_dungeon_level([[30, 2], [15, 3], [10, 4]])
    item_chances['leather shirt'] = baseclasses.from_dungeon_level([[40, 1], [20, 2], [15, 3]])
    item_chances['scalemail'] = baseclasses.from_dungeon_level([[10, 1], [40, 2], [30, 3], [15, 4]])
    item_chances['chainmail'] = baseclasses.from_dungeon_level([[40, 3], [30, 4]])
    item_chances['breastplate'] = baseclasses.from_dungeon_level([[15, 4]])

    choice = baseclasses.random_choice(item_chances)
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

def random_potion(point = None):
    item_chances = {}
    item_chances['heal'] = 40

    choice = baseclasses.random_choice(item_chances)
    if choice == 'heal':
        #create a healing potion
        item_component = Item(use_function=tome.cast_heal)
        item = Object(point, '!', 'healing potion', libtcod.violet, item=item_component)

    return item

def random_scroll(point = None):
    item_chances = {}
    item_chances['lightning'] = 40
    item_chances['fireball'] = 30
    item_chances['confuse'] = 30

    choice = baseclasses.random_choice(item_chances)
    if choice == 'lightning':
        item = lighting_scroll(point)

    elif choice == 'fireball':
        item = fireball_scroll(point)

    elif choice == 'confuse':
        item = confusion_scroll(point)

    return item

def random_weapon(point = None):
    item_chances = {}
    item_chances['dagger'] = baseclasses.from_dungeon_level([[60, 1], [40, 2], [20, 3], [10, 4]])
    item_chances['short sword'] = baseclasses.from_dungeon_level([[30, 1], [40, 2], [45, 3], [40, 4]])
    item_chances['long sword'] = baseclasses.from_dungeon_level([[10, 1], [20, 2], [35, 3], [40, 4], [60, 5]])

    choice = baseclasses.random_choice(item_chances)
    if choice == 'dagger':
        item = dagger(point)

    elif choice == 'short sword':
        item = shortsword(point)

    elif choice == 'long sword':
        item = longsword(point)

    return item

def random_magic_weapon():
    item = random_weapon(None)

    dice = libtcod.random_get_int(0, 1, 1000)

    if (dice <= 500):
        item.name = item.name + " of Stabby Stabby"
        item.color = libtcod.chartreuse
        item.equipment.power_bonus = item.equipment.power_bonus * 1.25
    elif (dice <= 750):
        item.name = item.name + " of YORE MA"
        item.color = libtcod.blue
        item.equipment.power_bonus = item.equipment.power_bonus * 1.5
    elif (dice <= 990):
        item.name = item.name + " of I'll FUCKING Have You"
        item.color = libtcod.purple
        item.equipment.power_bonus = item.equipment.power_bonus * 2
    else:
        item.name = item.name + " of Des and Troy"
        item.color = libtcod.crimson
        item.equipment.power_bonus = item.equipment.power_bonus * 4

    item.equipment.number_of_dice = 2

    return item

def lighting_scroll(point = None):
    #create a lightning bolt scroll
    item_component = Item(use_function=tome.cast_lightning)
    item = Object(point, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

    return item

def fireball_scroll(point = None):
    #create a fireball scroll
    item_component = Item(use_function=tome.cast_fireball)
    item = Object(point, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

    return item

def confusion_scroll(point = None):
    #create a confuse scroll
    item_component = Item(use_function=tome.cast_confuse)
    item = Object(point, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

    return item

def shield(point = None):
    #create a shield
    equipment_component = Equipment(EquipmentSlots.OFF_HAND, defense_bonus=1)
    item = Object(point, '[', 'shield', libtcod.darker_orange, gear=equipment_component)

    return item

def helmet(point = None):
    #create a helmet
    equipment_component = Equipment(EquipmentSlots.HEAD, defense_bonus=1)
    item = Object(point, '^', 'helmet', libtcod.darker_orange, gear=equipment_component)

    return item

def leathershirt(point = None):
    #create a chainmail
    equipment_component = Equipment(EquipmentSlots.CHEST, 1)
    item = Object(point, '=', 'leather shirt', libtcod.sky, gear=equipment_component)

    return item

def scalemail(point = None):
    #create a chainmail
    equipment_component = Equipment(EquipmentSlots.CHEST, 2)
    item = Object(point, '=', 'scalemail', libtcod.sky, gear=equipment_component)

    return item

def chainmail(point = None):
    #create a chainmail
    equipment_component = Equipment(EquipmentSlots.CHEST, 3)
    item = Object(point, '=', 'chainmail', libtcod.sky, gear=equipment_component)

    return item

def breastplate(point = None):
    #create a breastplate
    equipment_component = Equipment(EquipmentSlots.CHEST, 4)
    item = Object(point, '=', 'breastplate', libtcod.sky, gear=equipment_component)

    return item

def dagger(point = None):
    #create a sword
    equipment_component = Equipment(EquipmentSlots.MAIN_HAND, 2)
    equipment_component.type_of_dice = 4
    item = Object(point, '-', 'dagger', libtcod.sky, gear=equipment_component)

    return item

def shortsword(point = None):
    #create a sword
    equipment_component = Equipment(EquipmentSlots.MAIN_HAND, 3)
    equipment_component.type_of_dice = 6
    item = Object(point, '/', 'short sword', libtcod.sky, gear=equipment_component)

    return item

def longsword(point = None):
    #create a sword
    equipment_component = Equipment(EquipmentSlots.MAIN_HAND, 4)
    equipment_component.type_of_dice = 8
    item = Object(point, '\\', 'long sword', libtcod.sky, gear=equipment_component)

    return item
