import logging

import pubsub

from math import floor

from game_messages import Message

from etc.colors import COLORS
from etc.enum import DamageType, HealthStates, MessageType, ResultTypes

class Health:
    def __init__(self, hp):
        self.base_max_hp = hp
        self.hp = hp
        self.on_death = None

    def __str__(self):
        return f"{self.hp}/{self.base_max_hp}"

    def __repr__(self):
        return f"{self.hp}/{self.base_max_hp}"

    @property
    def dead(self):
        return (self.hp <= 0)

    @property
    def health_percentage(self):
        return ((self.hp * 100) // self.max_hp)

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    def take_damage(self, amount, npc = None, type=DamageType.DEFAULT):
        results = []

        total_damage = 0

        if self.dead:
            return results, total_damage

        if self.owner.damagemodifier:
            amount = floor(amount * self.owner.damagemodifier.modifier(type))

        total_damage = min(self.hp, amount)

        results.append({ResultTypes.DAMAGE: total_damage})
        self.hp -= amount

        if self.dead:
            logging.info(f"Death of {self.owner} by {npc}")

            self.hp = 0

            if npc and npc.ai:
                npc.ai.remove_target(self.owner)

            message = Message(f"{self.owner.name.title()} is dead!", COLORS.get('death_text'), source=self.owner, target=npc, type=MessageType.COMBAT)
            results.append({ResultTypes.MESSAGE: message})
            results.append({ResultTypes.DEAD_ENTITY: {'dead': self.owner, 'attacker': npc}})

            if npc and self.owner.level:
                xp = self.owner.level.xp_worth(npc)
                results.extend([{ResultTypes.EARN_XP: {'xp': xp, 'earner': npc}}])

            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.DEATH, target=npc))

        else:
            if self.owner.sleep:
                self.owner.sleep.end()
            if npc and self.owner.ai:
                self.owner.ai.set_target(npc)

        return results, total_damage

    def heal(self, amt):
        results = []
        if self.dead:
            return results

        self.hp += amt
        if (self.hp > self.base_max_hp):
            self.hp = self.base_max_hp

        suffix = ''
        if amt > 1:
            suffix = 's'

        results.append({
            ResultTypes.MESSAGE: Message('{1} heals for {0} point{2}.'.format(amt ,self.owner.name.title(), suffix), COLORS.get('effect_text'), target=self.owner, type=MessageType.EFFECT)
        })

        return results

    def display_color(self):

        if (self.health_percentage <= HealthStates.NEAR_DEATH):
            return COLORS.get('health_near_death')
        elif (self.health_percentage <= HealthStates.INJURED):
            return COLORS.get('health_injured')
        elif (self.health_percentage <= HealthStates.BARELY_INJURED):
            return COLORS.get('health_barely_injured')

        return self.owner.color
