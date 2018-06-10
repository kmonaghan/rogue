import libtcodpy as libtcod
import messageconsole
import pc
import baseclasses
import tome

import game_state

from equipment_slots import EquipmentSlots

class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self, npc):
        #add to the player's inventory and remove from the map
        if len(npc.inventory) >= 26:
            messageconsole.message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            npc.add_to_inventory(self.owner)
            game_state.objects.remove(self.owner)
            if (npc == pc.player):
                messageconsole.message('You picked up a ' + self.owner.name + '!', libtcod.green)

            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and npc.get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def drop(self):
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        npc = self.owner.owner
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        game_state.objects.append(self.owner)
        npc.remove_from_inventory(self.owner)
        self.owner.x = npc.x
        self.owner.y = npc.y
        if (npc == pc.player):
            messageconsole.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

    def examine(self):
        self.owner.examine()

    def use(self):
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        #just call the "use_function" if it is defined
        if self.use_function is None:
            return
            messageconsole.message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                pc.player.inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.number_of_dice = 1
        self.type_of_dice = 6
        self.bonus_damage = 0
        self.slot = slot
        self.is_equipped = False

    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = self.owner.owner.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        if (self.owner.owner == pc.player):
            #messageconsole.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
            messageconsole.message('Equipped ' + self.owner.name + '.', libtcod.light_green)

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        if (self.owner.owner == pc.player):
#            messageconsole.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)
            messageconsole.message('Dequipped ' + self.owner.name + '.', libtcod.light_yellow)

    def damage(self):
        total = self.bonus_damage

        for x in range(0, self.number_of_dice):
            total += libtcod.random_get_int(0, 1, self.type_of_dice)

        return total

    def damage_description(self):
        base = 'Damage: ' + str(self.number_of_dice) + 'd' + str(self.type_of_dice)

        if (self.bonus_damage):
            base += ' +' + str(self.bonus_damage)

        return base

    def equipment_description(self):
        desription = ""
        if (self.number_of_dice):
            description = self.damage_description()

        return description

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
        item = baseclasses.Object(point, '!', 'healing potion', libtcod.violet, item=item_component)

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
    item = baseclasses.Object(point, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

    return item

def fireball_scroll(point = None):
    #create a fireball scroll
    item_component = Item(use_function=tome.cast_fireball)
    item = baseclasses.Object(point, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

    return item

def confusion_scroll(point = None):
    #create a confuse scroll
    item_component = Item(use_function=tome.cast_confuse)
    item = baseclasses.Object(point, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

    return item

def shield(point = None):
    #create a shield
    equipment_component = Equipment(EquipmentSlots.OFF_HAND, defense_bonus=1)
    item = baseclasses.Object(point, '[', 'shield', libtcod.darker_orange, gear=equipment_component)

    return item

def helmet(point = None):
    #create a helmet
    equipment_component = Equipment(EquipmentSlots.HEAD, defense_bonus=1)
    item = baseclasses.Object(point, '^', 'helmet', libtcod.darker_orange, gear=equipment_component)

    return item

def leathershirt(point = None):
    #create a chainmail
    equipment_component = Equipment(EquipmentSlots.CHEST, 1)
    item = baseclasses.Object(point, '=', 'leather shirt', libtcod.sky, gear=equipment_component)

    return item

def scalemail(point = None):
    #create a chainmail
    equipment_component = Equipment(EquipmentSlots.CHEST, 2)
    item = baseclasses.Object(point, '=', 'scalemail', libtcod.sky, gear=equipment_component)

    return item

def chainmail(point = None):
    #create a chainmail
    equipment_component = Equipment(EquipmentSlots.CHEST, 3)
    item = baseclasses.Object(point, '=', 'chainmail', libtcod.sky, gear=equipment_component)

    return item

def breastplate(point = None):
    #create a breastplate
    equipment_component = Equipment(EquipmentSlots.CHEST, 4)
    item = baseclasses.Object(point, '=', 'breastplate', libtcod.sky, gear=equipment_component)

    return item

def dagger(point = None):
    #create a sword
    equipment_component = Equipment(EquipmentSlots.MAIN_HAND, 2)
    equipment_component.type_of_dice = 4
    item = baseclasses.Object(point, '-', 'dagger', libtcod.sky, gear=equipment_component)

    return item

def shortsword(point = None):
    #create a sword
    equipment_component = Equipment(EquipmentSlots.MAIN_HAND, 3)
    equipment_component.type_of_dice = 6
    item = baseclasses.Object(point, '/', 'short sword', libtcod.sky, gear=equipment_component)

    return item

def longsword(point = None):
    #create a sword
    equipment_component = Equipment(EquipmentSlots.MAIN_HAND, 4)
    equipment_component.type_of_dice = 8
    item = baseclasses.Object(point, '\\', 'long sword', libtcod.sky, gear=equipment_component)

    return item
