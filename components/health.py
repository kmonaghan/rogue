import tcod

import pubsub

from game_messages import Message

from etc.colors import COLORS
from etc.enum import ResultTypes, HealthStates

class Health:
    def __init__(self, hp):
        self.base_max_hp = hp
        self.hp = hp

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

    def take_damage(self, amount, npc = None):
        results = []

        if self.dead:
            return results

        self.hp -= amount
        if self.dead:
            self.hp = 0
            death_message = Message(f"{self.owner.name.title()} is dead!'", tcod.orange)
            print(f"Death of {self.owner.name} - {self.owner.uuid}")
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = death_message))
            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.DEATH, target=npc))
            if npc and npc.ai:
                npc.ai.remove_target()
            results.append({ResultTypes.DEAD_ENTITY: self.owner})
        elif npc and self.owner.ai:
            print("Set the attacker")
            self.owner.ai.set_target(npc)

        return results

    def heal(self, amt):
        if self.dead:
            return

        self.hp += amt
        if (self.hp > self.base_max_hp):
            self.hp = self.base_max_hp

    def display_color(self):

        if (self.health_percentage <= HealthStates.NEAR_DEATH):
            return tcod.red
        elif (self.health_percentage <= HealthStates.INJURED):
            return tcod.orange
        elif (self.health_percentage <= HealthStates.BARELY_INJURED):
            return tcod.yellow

        return self.owner.color
