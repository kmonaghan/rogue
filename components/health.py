import tcod

import pubsub

from game_messages import Message

from etc.colors import COLORS
from etc.enum import ResultTypes

class Health:
    def __init__(self, hp):
        self.base_max_hp = hp
        self.hp = hp
        self.dead = False

    @property
    def health_percentage(self):
        return ((self.hp * 100) / self.max_hp)

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    def take_damage(self, amount, npc = None):
        results = []

        if (self.dead):
            return results

        self.hp -= amount
        if (self.hp <= 0):
            self.dead = True
            self.hp = 0
            death_message = Message('{0} is dead!'.format(self.owner.name.title()), tcod.orange)
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = death_message))
            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.DEATH, target=npc))

        if npc and self.owner.ai:
            self.owner.ai.set_target(npc)

        if self.dead:
            if npc:
                npc.ai.remove_target()
            results.append({ResultTypes.DEAD_ENTITY: self.owner})

        return results

    def heal(self, amt):
        if (self.dead):
            return

        self.hp += amt
        if (self.hp > self.base_max_hp):
            self.hp = self.base_max_hp

    def display_color(self):

        if (self.health_percentage <= 20):
            return tcod.red
        elif (self.health_percentage <= 60):
            return tcod.orange
        elif (self.health_percentage <= 80):
            return tcod.yellow

        return self.owner.color
