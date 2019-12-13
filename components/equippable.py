from utils.random_utils import die_roll

class Equippable:
    def __init__(self, slot, power_bonus=0, defence_bonus=0, max_hp_bonus=0, bonus_damage=0, attribute=None):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defence_bonus = defence_bonus
        self.max_hp_bonus = max_hp_bonus
        self.bonus_damage = bonus_damage
        self.number_of_dice = 1
        self.type_of_dice = 6
        self.bonus_damage = 0
        self.attribute=attribute

    def damage(self):
        return die_roll(self.number_of_dice, self.type_of_dice, self.bonus_damage)

    def damage_description(self):
        base = 'Damage: ' + str(self.number_of_dice) + 'd' + str(self.type_of_dice)

        if (self.bonus_damage):
            base += ' +' + str(self.bonus_damage)

        return base

    def on_equip(self, entity):
        if self.attribute:
            entity.add_component(self.attribute, type(self.attribute).__name__)
            self.attribute.start()

    def on_dequip(self, entity):
        if self.attribute:
            self.attribute.end()
            entity.del_component(type(self.attribute).__name__)

    def equipment_description(self):
        desription = ""
        if (self.number_of_dice):
            description = self.damage_description()

        return description
