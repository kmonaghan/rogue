import libtcodpy as libtcod

from equipment_slots import EquipmentSlots

class Defence:
    def __init__(self, defence = 0):
        self.base_defence = defence
        self.owner = None

    @property
    def defence(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defence_bonus
        else:
            bonus = 0

        return self.base_defence + bonus
