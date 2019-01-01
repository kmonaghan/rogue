import libtcodpy as libtcod

import pubsub
from game_messages import Message


class Berserk:
    def __init__(self, defence_modifier = 0.75, power_modifier = 1.5, health_modifier = 10, turns = 10):
        self.defence_modifier = defence_modifier
        self.power_modifier = power_modifier
        self.health_modifier = health_modifier
        self.turns = turns
        pubsub.pubsub.add_subscription(pubsub.Subscription(self, pubsub.PubSubTypes.TICK, self.countdown))

    def countdown(self, sub, message, fov_map, game_map):
        self.turns -= 1
        if (self.turns < 1):
            self.end_berserker()
            pubsub.pubsub.mark_subscription_for_removal(sub)
            self.owner.del_component("berserk")

    def start_berserker(self):
        self.owner.health.base_max_hp += 10
        self.owner.health.heal(10)
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('{0} has gone berserk!'.format(self.owner.name.title()), libtcod.red)))

    def end_berserker(self):
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('{0} has regained their composure'.format(self.owner.name.title()), libtcod.green)))
        self.owner.health.base_max_hp -= 10
        self.owner.health.take_damage(10)
