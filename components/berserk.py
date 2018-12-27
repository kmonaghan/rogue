import libtcodpy as libtcod

import pubsub

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
            pubsub.pubsub.mark_subscription_for_removal(sub)
            self.owner.del_component("berserk")
