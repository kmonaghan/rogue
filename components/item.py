import libtcodpy as libtcod

import game_state
import messageconsole

from equipment_slots import EquipmentSlots

class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function

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
