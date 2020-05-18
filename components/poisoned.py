import logging

import pubsub

from etc.colors import COLORS
from etc.enum import DamageType, MessageType, ResultTypes

from game_messages import Message

class Poisoned:
    def __init__(self, damage_per_turn=1, duration=1, poisoner=None):
        self.owner = None
        self.damage_per_turn = damage_per_turn
        self.duration = duration
        self.uuid = None
        self.poisoner = poisoner

    def tick(self, game_map):
        self.duration -= 1
        results = []

        if self.owner.health.dead:
            self.end()
            return results

        damage_results, total_damage = self.owner.health.take_damage(self.damage_per_turn, type=DamageType.POISON, npc=self.poisoner)
        results.extend(damage_results)
        results.append({
            ResultTypes.MESSAGE: Message(f"The poison does {total_damage} damage to {self.owner.name.title()}", COLORS.get('damage_text'), target=self.owner, type=MessageType.EFFECT)
        })

        if (self.duration == 0):
            results.extend(self.end())

        return results

    def start(self):
        results = []

        results.append({
            ResultTypes.MESSAGE: Message(f"{self.owner.name.title()} feels something is wrong...their veins are on fire...hopefully they can outlast it", COLORS.get('effect_text'), target=self.owner, type=MessageType.EFFECT)
        })

        self.uuid = self.owner.register_turn(self)

        return results

    def end(self):
        results = []

        if self.owner:
            try:
                self.owner.del_component("poisoned")
            except AttributeError:
                logging.info(f"Tried to remove poison from {self.owner.name} - {self.owner.uuid}")
        else:
            logging.info('****No owner to poisoned - already deleted?')

        self.owner.deregister_turn(self.uuid)

        if not self.owner.health.dead:
            results.append({
                ResultTypes.MESSAGE: Message(f"The poison has run its course in {self.owner.name.title()}", COLORS.get('effect_text'), target=self.owner, type=MessageType.EFFECT)
            })

        return results
