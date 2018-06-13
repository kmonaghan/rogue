import libtcodpy as libtcod

import game_state
import messageconsole

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
            if (npc == game_state.player):
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
        if (npc == game_state.player):
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
                game_state.player.inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason
