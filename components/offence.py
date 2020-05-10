from operator import itemgetter
from random import randint

from etc.colors import COLORS
from etc.enum import EquipmentSlot, MessageType, ResultTypes

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

        total = randint(1, 20)
        multiplier = 1;
        if (total == 20):
            multiplier = 2

        total = total + self.power
        hit = total - target.defence.defence

        weapon = self.owner.equipment.get_equipped_in_slot(EquipmentSlot.MAIN_HAND)

        if (hit > 0) or (multiplier == 2):
            #make the target take some damage
            damage = weapon.equippable.damage() * multiplier
            damage_results, total_damage = target.health.take_damage(damage, self.owner, weapon.equippable.damage_type)
            results.extend(damage_results)

            msg_text = '{0} attacks {1} with {2} for {3} hit points.'
            if (multiplier > 1):
                msg_text = '{0} smashes {1} with a massive blow from their {2} for {3} hit points.'

            if total_damage > 0:
                message = Message(msg_text.format(self.owner.name.title(), target.name, weapon.name, str(total_damage)),
                                COLORS.get('damage_text'), source=self.owner, target=target, type=MessageType.COMBAT)
                results.append({ResultTypes.MESSAGE: message})

            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.ATTACKED, target=target))

            if weapon.ablity and not target.health.dead:
                if weapon.identifiable and not weapon.identified:
                    if randint(1,100) < weapon.identifiable.chance_to_identify:
                        return results
                    else:
                        weapon.identifiable.identified = True
                        message = Message(weapon.identifiable.identified_on_use_message, COLORS.get('success_text'), target=self.owner, type=MessageType.EFFECT)

                        results.append({ResultTypes.MESSAGE: message})

                results.extend(weapon.ablity.on_attack(source=self.owner, target=target))
        else:
            message = Message('{0} attacks {1} with {2} but does no damage.'.format(self.owner.name.title(), target.name, weapon.name), COLORS.get('damage_text'), source=self.owner,target=target, type=MessageType.COMBAT)
            results.append({ResultTypes.MESSAGE: message})

        return results
