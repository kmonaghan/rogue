from enum import Enum, auto

pubsub = None

class PubSubTypes(Enum):
    ATTACKED = auto()
    DEATH = auto()
    TICK = auto()
    MESSAGE = auto()

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

    def add_subscription(self, sub):
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

    def process_queue(self, fov_map, game_map):
        while self.queue:
            message = self.queue.pop()

            if message.type in self.subscriptions:
                for sub in self.subscriptions[message.type]:
                    sub.callback(sub, message, fov_map, game_map)

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
