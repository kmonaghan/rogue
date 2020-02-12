import pubsub

from etc.colors import COLORS
from etc.enum import ResultTypes

from game_messages import Message

class Regeneration:
    def __init__(self, heal_per_tick=1, turns_between_heals=1, duration=0):
        self.owner = None
        self.duration = duration
        self.heal_per_tick = heal_per_tick
        self.turns_between_heals = turns_between_heals
        self.turns_since_last_heal = 0
        self.uuid = None

    def tick(self, game_map):
        self.duration -= 1
        results = []

        if self.owner.health.dead:
            self.end()
            return results

        if self.owner.health.hp >= self.owner.health.base_max_hp:
            return results

        if self.turns_since_last_heal < self.turns_between_heals:
            self.turns_since_last_heal += 1
            return results

        results.extend(self.owner.health.heal(self.heal_per_tick))

        self.turns_since_last_heal = 0

        return results

    def start(self):
        results = []

        self.uuid = self.owner.register_turn(self)

        return results

    def end(self):
        results = []

        if self.owner:
            try:
                self.owner.del_component("regeneration")
            except AttributeError:
                print(f"tried to remove regeneration from {self.owner.name} - {self.owner.uuid}")
        else:
            print('****No owner to regeneration - already deleted?')

        self.owner.deregister_turn(self.uuid)

        return results
