import pubsub

from etc.colors import COLORS
from etc.enum import ResultTypes

from game_messages import Message

class Berserk:
    def __init__(self, defence_modifier = 0.75, power_modifier = 1.5, health_modifier = 10, turns = 10):
        self.defence_modifier = defence_modifier
        self.power_modifier = power_modifier
        self.health_modifier = health_modifier
        self.turns = turns
        self.uuid = None

    def tick(self):
        results = []

        self.turns -= 1
        if (self.turns < 1):
            results.extend(self.end())

        return results

    def start(self):
        results = []

        self.owner.health.base_max_hp += self.health_modifier
        self.owner.health.heal(self.health_modifier)
        results.append({
            ResultTypes.MESSAGE: Message('{0} has gone berserk!'.format(self.owner.name.title()), COLORS.get('effect_text'))
        })

        self.uuid = self.owner.register_turn(self)

        return results

    def end(self):
        results = []
        if not self.owner.health.dead:
            results.append({
                ResultTypes.MESSAGE: Message('{0} has regained their composure'.format(self.owner.name.title()), COLORS.get('effect_text'))
            })
            self.owner.health.base_max_hp -= self.health_modifier
            damage_results, total_damage = self.owner.health.take_damage(self.health_modifier)
            results.extend(damage_results)

            self.owner.deregister_turn(self.uuid)

            try:
                self.owner.del_component('berserk')
            except AttributeError:
                print(f"tried to remove berserk from {self.owner.name} - {self.owner.uuid}")

        return results
