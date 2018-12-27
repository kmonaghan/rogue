from enum import Enum, auto

pubsub = None

class PubSubTypes(Enum):
    ATTACKED = auto()
    DEATH = auto()
    TICK = auto()

class Publish:
    def __init__(self, entity, type, target = None, priority = 0):
        self.entity = entity
        self.type = type
        self.priority = priority
        self.target = target

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
        self.subscriptions[sub.type].remove(sub)

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
