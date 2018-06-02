import libtcodpy as libtcod
import messageconsole
import pc
import baseclasses
import tome

inventory = []

class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            messageconsole.message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            baseclasses.objects.remove(self.owner)
            messageconsole.message('You picked up a ' + self.owner.name + '!', libtcod.green)

            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def drop(self):
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        baseclasses.objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = pc.player.x
        self.owner.y = pc.player.y
        messageconsole.message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

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
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

        self.slot = slot
        self.is_equipped = False

    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        messageconsole.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        messageconsole.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)


def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj):  #returns a list of equipped items
    if obj == pc.player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  #other objects have no equipment

def random_potion(x,y):
    item_chances = {}
    item_chances['heal'] = 40

    choice = baseclasses.random_choice(item_chances)
    if choice == 'heal':
        #create a healing potion
        item_component = Item(use_function=tome.cast_heal)
        item = baseclasses.Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)

    return item

def random_scroll(x,y):
    item_chances = {}
    item_chances['lightning'] = 40
    item_chances['fireball'] = 30
    item_chances['confuse'] = 30

    choice = baseclasses.random_choice(item_chances)
    if choice == 'lightning':
        #create a lightning bolt scroll
        item_component = Item(use_function=tome.cast_lightning)
        item = baseclasses.Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

    elif choice == 'fireball':
        #create a fireball scroll
        item_component = Item(use_function=tome.cast_fireball)
        item = baseclasses.Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

    elif choice == 'confuse':
        #create a confuse scroll
        item_component = Item(use_function=tome.cast_confuse)
        item = baseclasses.Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

    return item
