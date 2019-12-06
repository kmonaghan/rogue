import pubsub

from etc.colors import COLORS

from game_messages import Message

class Spawn:
    def __init__(self, energy_needed=2, npc=None):
        self.current_energy = 0
        self.spawn_energy = energy_needed
        self.npc = npc

    @property
    def can_spawn(self):
        return (self.current_energy >= self.spawn_energy)

    def increase_energy(self, amount = 1):
        self.current_energy += amount
        if self.can_spawn:
            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.SPAWN))

    def spawn(self):
        if not self.owner.health.dead:
            spawned = self.npc(self.owner.point)
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('{0} has spawned a '.format(self.owner.name.title(), spawned.name.title()), COLORS.get('effect_text'))))
            self.current_energy = 0
            return spawned

        return None
