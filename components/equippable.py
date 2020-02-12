from etc.enum import DamageType

from utils.random_utils import die_roll

class Equippable:
    def __init__(self, slot, power_bonus=0, defence_bonus=0, max_hp_bonus=0, bonus_damage=0, attribute=None, damage_type=DamageType.DEFAULT):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defence_bonus = defence_bonus
        self.max_hp_bonus = max_hp_bonus
        self.bonus_damage = bonus_damage
        self.number_of_dice = 1
        self.type_of_dice = 6
        self.bonus_damage = 0
        self.attribute=attribute
        self.damage_type = damage_type

    def damage(self):
        return die_roll(self.number_of_dice, self.type_of_dice, self.bonus_damage)

    def damage_description(self):
        base = 'Damage: ' + str(self.number_of_dice) + 'd' + str(self.type_of_dice)

        if (self.bonus_damage):
            base += ' +' + str(self.bonus_damage)

        return base

    def on_equip(self, entity):
        print(f"equiping {self}")
        print(entity)
        if self.attribute:
            entity.add_component(self.attribute, type(self.attribute).__name__)
            self.attribute.start()
        if self.owner.aura:
            print('adding aura')
            self.owner.aura.owner = entity
            self.owner.aura.uuid = entity.register_turn(self.owner.aura)
            print(f"aura uuid: {self.owner.aura.uuid}")
            entity.aura = True

    def on_dequip(self, entity):
        print('dequip')
        print(entity)
        if self.attribute:
            self.attribute.end()
            entity.del_component(type(self.attribute).__name__)
        if self.owner.aura:
            print('removing aura')
            self.owner.aura.owner = None
            entity.deregister_turn(self.owner.aura.uuid)
            entity.aura = False

    def equipment_description(self):
        desription = ""
        if (self.number_of_dice):
            description = self.damage_description()

        return description
