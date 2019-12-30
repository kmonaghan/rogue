import pubsub

from etc.colors import COLORS
from etc.enum import ResultTypes

from game_messages import Message

class Poisoned:
    def __init__(self, damage_per_turn=1, duration=1):
        self.owner = None
        self.damage_per_turn = damage_per_turn
        self.duration = duration
        self.uuid = None

    def tick(self):
        self.duration -= 1
        results = []

        if self.owner.health.dead:
            self.end()
            return results

        damage_results, total_damage = self.owner.health.take_damage(self.damage_per_turn)
        results.extend(damage_results)
        results.append({
            ResultTypes.MESSAGE: Message('The poison does {0} damage to {1}'.format(total_damage ,self.owner.name.title()), COLORS.get('damage_text'))
        })

        if (self.duration == 0):
            results.extend(self.end())

        return results

    def start(self):
        results = []

        results.append({
            ResultTypes.MESSAGE: Message('{0} feels something is wrong...their veins are on fire...hopefully they can outlast it'.format(self.owner.name.title()), COLORS.get('effect_text'))
        })

        self.uuid = self.owner.register_turn(self)

        return results

    def end(self):
        results = []

        if self.owner:
            try:
                self.owner.del_component("poisoned")
            except AttributeError:
                print(f"tried to remove posion from {self.owner.name} - {self.owner.uuid}")
        else:
            print('****No owner to poisoned - already deleted?')

        self.owner.deregister_turn(self.uuid)

        if not self.owner.health.dead:
            results.append({
                ResultTypes.MESSAGE: Message('The poison has run its course in {0}.'.format(self.owner.name.title()), COLORS.get('effect_text'))
            })

        return results
