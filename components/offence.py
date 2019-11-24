from random import randint

import tcod as libtcod

from equipment_slots import EquipmentSlots
from game_messages import Message

import pubsub

class Offence:
    def __init__(self, base_power = 0):
        self.base_power = base_power
        self.owner = None

    @property
    def power(self):
        multiplier = 1

        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        if self.owner.subspecies:
            bonus += self.owner.subspecies.bonus_power

        if self.owner.berserk:
            multiplier = self.owner.berserk.power_modifier

        return (self.base_power + bonus) * multiplier

    def attack(self, target):
        results = []

        #a simple formula for attack damage
        total = randint(1, 20)
        multiplier = 1;
        if (total == 20):
            multiplier = 2

        total = total + self.power
        hit = total - target.defence.defence

        weapon = self.owner.equipment.get_equipped_in_slot(EquipmentSlots.MAIN_HAND)

        if (hit > 0) or (multiplier == 2):
            #make the target take some damage
            damage = weapon.equippable.damage() * multiplier

            msg_text = '{0} attacks {1} with {2} for {3} hit points.'
            if (multiplier > 1):
                msg_text = '{0} smashes {1} with a massive blow from their {2} for {3} hit points.'

            msg = Message(msg_text.format(self.owner.name.title(), target.name, weapon.name, str(damage)), libtcod.white)
            results.extend(target.health.take_damage(damage, self.owner))

            if weapon.poisoner:
                weapon.poisoner.attacked_target(target)

            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.ATTACKED, target=target))
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = msg))

        else:
            msg = Message('{0} attacks {1} with {2} but does no damage.'.format(self.owner.name.title(), target.name, weapon.name), libtcod.white)
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = msg))

        return results
