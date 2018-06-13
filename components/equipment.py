import libtcodpy as libtcod

import game_state
import messageconsole

from equipment_slots import EquipmentSlots

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
        if (self.owner.owner == game_state.player):
            #messageconsole.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
            messageconsole.message('Equipped ' + self.owner.name + '.', libtcod.light_green)

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        if (self.owner.owner == game_state.player):
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
