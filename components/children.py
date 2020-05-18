import logging

import pubsub
from game_messages import Message

class Children:
    def __init__(self, max_children = 10):
        self.max_children = max_children
        self.children = []
        self.owner = None

        pubsub.pubsub.subscribe(pubsub.Subscription(self, pubsub.PubSubTypes.DEATH, self.possibleChildDeath))

    def __str__(self):
        nl = '\n'
        return f"Children:{nl} {nl.join(self.children)}"

    def __iter__(self):
        yield from self.children

    @property
    def number_of_children(self):
        return len(self.children)

    @property
    def can_have_children(self):
        return len(self.children) < self.max_children

    def possibleChildDeath(self, sub, message, game_map):
        if message.target is None:
            logging.info("Children.possibleChildDeath: the target is none?")
            return

        if sub.entity is None:
            logging.info("Children.possibleChildDeath: the subscriber is none?")
            return

        if message.entity.uuid in self.children:
            self.removeChild(message.entity)

    def addChild(self, entity):
        if self.can_have_children:
            self.children.append(entity.uuid) if entity.uuid not in self.children else self.children
            return True
        return False

    def removeChild(self, entity):
        self.children.remove(entity.uuid) if entity.uuid in self.children else self.children
