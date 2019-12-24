from random import randint

import tcod

from etc.colors import COLORS
from utils.random_utils import from_dungeon_level, random_choice_from_dict
import tome

from components.ablity import ExtraDamage, Poisoning, PushBack
from components.equippable import Equippable
from components.identifiable import Identifiable
from components.item import Item
from components.regeneration import Regeneration
from components.usable import AntidoteUsable, DefencePotionUsable, HealingPotionUsable, PowerPotionUsable, ScrollUsable
from components.unlock import Unlock

from entities.entity import Entity

from game_messages import Message

from tome import cast_confuse, cast_fireball, cast_identify, cast_lightning, heal, cast_mapping, cast_teleport

from equipment_slots import EquipmentSlots
from etc.enum import DamageType, Interactions, RenderOrder

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
    item_chances['offence'] = 40
    item_chances['defence'] = 40
    item_chances['antidote'] = 40

    choice = random_choice_from_dict(item_chances)
    if choice == 'heal':
        item = healing_potion(point)
    elif choice == 'offence':
            item = power_potion(point)
    elif choice == 'defence':
        item = defence_potion(point)
    elif choice == 'antidote':
        item = antidote_potion(point)

    return item

def random_ring(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['power'] = 50
    item_chances['defence'] = 50
    item_chances['regeneration'] = 5

    choice = random_choice_from_dict(item_chances)
    if choice == 'power':
        item = ring_of_power(point)

    elif choice == 'defence':
        item = ring_of_defence(point)
    elif choice == 'regeneration':
        item = ring_of_regeneration(point)
    return item

def random_scroll(point = None, dungeon_level = 1):
    item_chances = {}
    item_chances['lightning'] = 40
    item_chances['fireball'] = 30
    item_chances['confuse'] = 30
    item_chances['map_scroll'] = 20
    item_chances['identify_scroll'] = 20
    item_chances['teleport'] = 20

    choice = random_choice_from_dict(item_chances)
    if choice == 'lightning':
        item = lighting_scroll(point)

    elif choice == 'fireball':
        item = fireball_scroll(point)

    elif choice == 'confuse':
        item = confusion_scroll(point)

    elif choice == 'map_scroll':
        item = map_scroll(point)

    elif choice == 'identify_scroll':
        item = identify_scroll(point)

    elif choice == 'teleport':
        item = teleport_scroll(point)

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

    item.add_component(Identifiable(),"identifiable")

    add_random_ablity(item)

    return item

def add_random_ablity(item):
    dice = randint(1, 100)

    if dice <=40:
        return
    elif dice <= 60:
        add_poison(item, 1, 10)
    elif dice <= 80:
        add_shocking(item)
    elif dice <= 100:
        add_smashing(item)

def add_poison(item, damage = 1, duration = 10):
    item.add_component(Poisoning(0, damage, duration), 'ablity')
    item.base_name = item.base_name + " of poisoning"

def add_flaming(item):
    item.add_component(ExtraDamage(number_of_dice=1, type_of_dice=6, name="fire", damage_type=DamageType.FIRE), 'ablity')
    item.base_name = item.base_name + " of flaming"

def add_shocking(item):
    item.add_component(ExtraDamage(number_of_dice=1, type_of_dice=6, name="shock", damage_type=DamageType.ELECTRIC), 'ablity')
    item.base_name = item.base_name + " of shocking"

def add_smashing(item):
    item.add_component(PushBack(), 'ablity')
    item.base_name = item.base_name + " of smashing"

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

def ring_of_regeneration(point = None):
    equippable_component = Equippable(EquipmentSlots.RING, attribute=Regeneration())
    item = Entity(point, 'o', 'Ring of Regeneration', COLORS.get('equipment_rare'), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
    return item

def antidote_potion(point = None):
    item = Entity(point, '!', 'Antidote', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=AntidoteUsable())

    return item

def healing_potion(point = None):
    item = Entity(point, '!', 'Healing Potion', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=HealingPotionUsable())

    return item

def power_potion(point = None):
    item = Entity(point, '!', 'Power Potion', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=PowerPotionUsable())

    return item

def defence_potion(point = None):
    item = Entity(point, '!', 'Defence Potion', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=Item(), usable=DefencePotionUsable())

    return item

def lighting_scroll(point = None):
    #create a lightning bolt scroll
    item_component = Item(use_function=cast_lightning, number_of_dice=2, type_of_dice=10, maximum_range=5)
    item = Entity(point, '#', 'Lightning Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def fireball_scroll(point = None):
    #create a fireball scroll
    usable = ScrollUsable(scroll_name="Fireball Scroll",
                            scroll_spell=cast_fireball,
                            number_of_die=3,
                            type_of_die=6,
                            radius=3,
                            targets_inventory=False)
    usable.needs_target = True
    usable.targeting_message = Message('Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan)

    item = Entity(point, '#', 'Fireball Scroll', COLORS.get('equipment_uncommon'), render_order=RenderOrder.ITEM,
                                  item=Item(), usable=usable)

    return item

def confusion_scroll(point = None):
    #create a confuse scroll
    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan))
    item = Entity(point, '#', 'Confusion Scroll', tcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=item_component)

    return item

def identify_scroll(point = None):
    usable = ScrollUsable(scroll_name="Identify Scroll", scroll_spell=cast_identify, targets_inventory=True)

    item = Entity(point, '#', usable.name, tcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

    return item

def teleport_scroll(point = None):
    usable = ScrollUsable(scroll_name="Teleport Scroll", scroll_spell=cast_teleport, targets_inventory=False)

    item = Entity(point, '#', usable.name, tcod.light_yellow, render_order=RenderOrder.ITEM,
                    item=Item(), usable=usable)

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
    equippable_component.damage_type = DamageType.SHARP
    item = Entity(point, '-', 'axe', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def dagger(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    equippable_component.type_of_dice = 4
    equippable_component.damage_type = DamageType.SHARP
    item = Entity(point, '-', 'dagger', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def shortsword(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
    equippable_component.type_of_dice = 6
    equippable_component.damage_type = DamageType.SHARP
    item = Entity(point, '/', 'short sword', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def longsword(point = None):
    #create a sword
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=4)
    equippable_component.type_of_dice = 8
    equippable_component.damage_type = DamageType.SHARP
    item = Entity(point, '\\', 'long sword', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def mace(point = None):
    #create a mace
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    equippable_component.type_of_dice = 10
    equippable_component.damage_type = DamageType.BLUNT
    item = Entity(point, '-', 'mace', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def teeth(point = None):
    #create teeth for animals
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    equippable_component.type_of_dice = 2
    equippable_component.damage_type = DamageType.SHARP
    item = Entity(point, '"', 'teeth', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def claw(point = None):
    #create claw for animals
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    equippable_component.type_of_dice = 4
    equippable_component.damage_type = DamageType.SHARP
    item = Entity(point, ',', 'claw', COLORS.get('equipment_uncommon'), equippable=equippable_component, render_order=RenderOrder.ITEM)

    return item

def key(point = None, unlocks = None):
    key = Entity(point, 'k', 'key', COLORS.get('light_door'),
                    blocks=False, interaction=Interactions.NONE,
                    render_order=RenderOrder.ITEM, item=Item())
    key.add_component(Unlock(unlocks.uuid), 'unlock')

    return key
