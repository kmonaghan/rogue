from equipment_slots import EquipmentSlots

class Defence:
    def __init__(self, defence = 0):
        self.base_defence = defence
        self.owner = None

    @property
    def defence(self):
        multiplier = 1

        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defence_bonus
        else:
            bonus = 0

        if self.owner.subspecies:
            bonus += self.owner.subspecies.bonus_defence

        if self.owner.berserk:
            multiplier = self.owner.berserk.defence_modifier

        return (self.base_defence + bonus) * multiplier
