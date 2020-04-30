from enum import Enum, auto

pubsub = None

class PubSubTypes(Enum):
    ATTACKED = auto()
    DEATH = auto()
    TICK = auto()
    MESSAGE = auto()
    EARNEDXP = auto()
    SPAWN = auto()

class Publish:
    def __init__(self, entity, type, target = None, priority = 0, message = None):
        self.entity = entity
        self.type = type
        self.priority = priority
        self.target = target
        self.message = message

class Subscription:
    def __init__(self, entity, type, callback):
        self.entity = entity
        self.type = type
        self.callback = callback

class PubSub:
    def __init__(self):
        self.subscriptions = {}
        self.queue = []
        self.for_removal = []

        self.subscribe(Subscription(None, PubSubTypes.DEATH, on_entity_death))
        self.subscribe(Subscription(None, PubSubTypes.SPAWN, entity_spawn))

    def subscribe(self, sub):
        if not sub.type in self.subscriptions:
            self.subscriptions[sub.type] = []

        self.subscriptions[sub.type].append(sub)

    def remove_subscription(self, sub):
        try:
            self.subscriptions[sub.type].remove(sub)
        except ValueError:
            pass

    def mark_subscription_for_removal(self, sub):
        self.for_removal.append(sub)

    def add_message(self, message):
        self.queue.append(message)

    def process_queue(self, game_map):
        while self.queue:
            message = self.queue.pop()

            if message.type in self.subscriptions:
                for sub in self.subscriptions[message.type]:
                    sub.callback(sub, message, game_map)

        for sub in self.for_removal:
            self.remove_subscription(sub)

        self.for_removal = []

    def unsubscribe_entity(self, entity):
        for subs in self.subscriptions:
            filtered = filter(lambda x: x.entity == entity, self.subscriptions[subs])
            for sub in filtered:
                self.mark_subscription_for_removal(sub)

        for sub in self.for_removal:
            self.remove_subscription(sub)

'''
Some default subscriptions
'''
def add_to_messages(sub, message, game_map):
    sub.entity.add_message(message.message, game_map)

def entity_spawn(sub, message, game_map):
    npc = message.entity.spawn.spawn()
    if npc:
        game_map.current_level.add_entity(npc)

def on_entity_death(sub, message, game_map):
    if sub.entity and sub.entity.ai:
        sub.entity.ai.remove_target(message.entity)
        pubsub.remove_subscription(sub)

    pubsub.unsubscribe_entity(message.entity)
