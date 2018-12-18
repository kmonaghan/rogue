import libtcodpy as libtcod

from equipment_slots import EquipmentSlots
from game_messages import Message

class Offense:
    def __init__(self, base_power = 0):
        self.base_power = base_power
        self.owner = None

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        return self.base_power + bonus

    def attack(self, target):
        results = []

        #a simple formula for attack damage
        total = libtcod.random_get_int(0, 1, 20)
        multiplier = 1;
        if (total == 20):
            multiplier = 2

        total = total + self.power
        hit = total - target.defence.defence

        weapon = self.owner.equipment.get_equipped_in_slot(EquipmentSlots.MAIN_HAND)

        if (hit > 0) or (multiplier == 2):
            #make the target take some damage
            damage = weapon.equippable.damage() * multiplier

            msg = '{0} attacks {1} with {2} for {3} hit points.'
            if (multiplier > 1):
                msg = '{0} smashes {1} with a massive blow from their {2} for {3} hit points.'

            results.append({'message': Message(msg.format(self.owner.name.title(), target.name, weapon.name, str(damage)), libtcod.white)})
            results.extend(target.health.take_damage(damage, self.owner))
        else:
            results.append({'message': Message('{0} attacks {1} with {2} but does no damage.'.format(
                self.owner.name.title(), target.name, weapon.name), libtcod.white)})

        return results
