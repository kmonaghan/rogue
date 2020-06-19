from etc.enum import DamageType

from utils.random_utils import die_roll

class Equippable:
    def __init__(self, slot, power=0, power_bonus= 0, defence=0, defence_bonus = 0,
                    max_hp_bonus=0, bonus_damage=0, attribute=None,
                    damage_type=DamageType.DEFAULT):
        self.slot = slot
        self._power = power
        self.power_bonus = power_bonus
        self._defence = defence
        self.defence_bonus = defence_bonus
        self.max_hp_bonus = max_hp_bonus
        self.bonus_damage = bonus_damage
        self.number_of_dice = 0
        self.type_of_dice = 0
        self.bonus_damage = 0
        self.attribute = attribute
        self.damage_type = damage_type

    def damage(self):
        """Calculate damage done in a hit."""
        return die_roll(self.number_of_dice, self.type_of_dice, self.bonus_damage)

    def damage_description(self):
        """Return a string describing how the damage delt by this item is calculated."""
        base = 'Damage: ' + str(self.number_of_dice) + 'd' + str(self.type_of_dice)

        if (self.bonus_damage):
            base += ' +' + str(self.bonus_damage)

        return base

    @property
    def defence(self):
        """Return the total defence bonus from this item."""
        return self._defence + self.defence_bonus

    @property
    def power(self):
        """Return the total power bonus from this item."""
        return self._power + self.power_bonus

    def on_equip(self, entity):
        """Apply any item effects to the equipping entity"""
        if self.owner.ablity:
            self.owner.ablity.on_equip(entity)
        if self.attribute:
            entity.add_component(self.attribute, type(self.attribute).__name__)
            self.attribute.start()
        if self.owner.aura:
            self.owner.aura.owner = entity
            self.owner.aura.uuid = entity.register_turn(self.owner.aura)
            entity.aura = True

    def on_dequip(self, entity):
        """Remove any item effects from the dequipping entity"""
        if self.owner.ablity:
            self.owner.ablity.on_dequip(entity)
        if self.attribute:
            self.attribute.end()
            entity.del_component(type(self.attribute).__name__)
        if self.owner.aura:
            self.owner.aura.owner = None
            entity.deregister_turn(self.owner.aura.uuid)
            entity.aura = False

    def equipment_description(self):
        """Return a string describing the item."""
        description = ""
        if self.number_of_dice:
            description += self.damage_description()
        elif self.defence:
            description += f"Defence: {self.defence}"

        return description
