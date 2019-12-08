import pubsub

from etc.colors import COLORS

from game_messages import Message

class Poisoned:
    def __init__(self, damage_per_turn=1, duration=1):
        self.owner = None
        self.damage_per_turn = damage_per_turn
        self.duration = duration

    def countdown(self, sub, message, game_map):
        self.duration -= 1

        if self.owner.health.dead or (self.duration < 0):
            self.end(sub)
            return

        self.owner.health.take_damage(self.damage_per_turn)
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('The poison does {0} damage to {1}'.format(self.damage_per_turn ,self.owner.name.title()), COLORS.get('damage_text'))))

        if (self.duration == 0):
            self.end(sub)
            return

    def start(self):
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('{0} feels something is wrong...their veins are on fire...hopefully they can outlast it'.format(self.owner.name.title()), COLORS.get('effect_text'))))

        pubsub.pubsub.subscribe(pubsub.Subscription(self, pubsub.PubSubTypes.TICK, self.countdown))

    def end(self, sub):
        if self.owner:
            try:
                self.owner.del_component("poisoned")
            except AttributeError:
                print(f"tried to remove posion from {self.owner.name} - {self.owner.uuid}")
        else:
            print('****No owner to poisoned - already deleted?')
        pubsub.pubsub.mark_subscription_for_removal(sub)
        if not self.owner.health.dead:
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('The poison has run its course in {0}.'.format(self.owner.name.title()), COLORS.get('effect_text'))))