import pubsub

from etc.colors import COLORS
from etc.enum import DamageType, MessageType, ResultTypes

from game_messages import Message

class Speed:
    def __init__(self, act_energy_adjustment=0.5, duration=10, damage_on_end=True):
        self.act_energy_adjustment = act_energy_adjustment
        self.act_energy_old = None
        self.damage_on_end = damage_on_end
        self.duration = self.total_duration = duration
        self.owner = None
        self.uuid = None

    def tick(self, game_map):
        self.duration -= 1
        results = []

        if (self.duration == 0):
            results.extend(self.end())

        return results

    def start(self):
        results = []

        self.act_energy_old = self.owner.energy.act_energy

        self.owner.energy.act_energy = max(1, self.owner.energy.act_energy * self.act_energy_adjustment)

        speed_direction = "speed up"
        if self.owner.energy.act_energy > self.act_energy_old:
            speed_direction = "slowed down"

        results.append({
            ResultTypes.MESSAGE: Message(f"Everything has {speed_direction} for {self.owner.name.title()}.", COLORS.get('effect_text'), target=self.owner, type=MessageType.EFFECT)
        })

        self.uuid = self.owner.register_turn(self)

        return results

    def end(self):
        results = []

        self.owner.energy.act_energy = self.act_energy_old

        self.owner.del_component("speed")

        self.owner.deregister_turn(self.uuid)

        results.append({
            ResultTypes.MESSAGE: Message(f"{self.owner.name.title()} returns to normal.", COLORS.get('effect_text'), target=self.owner, type=MessageType.EFFECT)
        })

        if self.damage_on_end:
            dmg = int(self.act_energy_adjustment * self.total_duration)
            damage_results, total_damage = self.owner.health.take_damage(dmg)
            results.extend(damage_results)
            results.append({ResultTypes.MESSAGE: Message(f"{self.owner.name.title()} takes {total_damage} damage.", COLORS.get('damage_text'), target=self.owner, type=MessageType.EFFECT)})
            results.append({ResultTypes.MESSAGE: Message(f"{self.owner.name.title()} feels drained and everything feels like it's in gel.", COLORS.get('effect_text'), target=self.owner, type=MessageType.EFFECT)})

        print(results)
        return results
