import libtcodpy as libtcod

class Equippable:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0, bonus_damage=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.bonus_damage = bonus_damage
        self.number_of_dice = 1
        self.type_of_dice = 6
        self.bonus_damage = 0

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