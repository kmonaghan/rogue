from random import choice

import bestiary

from game_messages import Message

from etc.colors import COLORS
from etc.enum import ResultTypes, Species, SPECIES_STRINGS, VERMIN_GENERATORS, RoutingOptions

import pubsub

active_quests = []

def kill_quest_npc_death(sub, message, game_map):
    if sub.entity.npc:
        if sub.entity.npc.uuid == message.entity.uuid:
            sub.entity.kill_count(message.entity)
    if (message.entity.species == sub.entity.kill_type) and (message.target.species == Species.PLAYER):
        sub.entity.kill_count(message.entity)

def check_quest_for_location(player):
    global active_quests

    results = []

    for quest in active_quests:
        if (quest.map_point):
            if (player.point == quest.map_point):
                quest.finish_quest()
                pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message=Message('Quest ' + quest.title + ' completed!', COLORS.get('success_text'))))
                pubsub.pubsub.add_message(pubsub.Publish(quest, pubsub.PubSubTypes.EARNEDXP, target=player))

    return results

class Quest:
    def __init__(self, title, description, xp, kill=0, kill_type=None, start_func = None, map_point = None, target_npc = None):
        self.title = title
        self.description = description
        self.xp = xp
        self.started = False
        self.kill = kill
        self.kill_type = kill_type
        self.kill_total = 0
        self.completed = False
        self.return_to_quest_giver = False
        self.next_quest = None
        self.npc = target_npc
        if self.npc:
            self.kill = 1
        self.start_func = start_func
        self.map_point = map_point

    def kill_count(self, npc):
        results = []

        if self.completed:
            return results

        if (self.kill == 0):
            return

        if self.npc == npc:
            self.kill_total += 1

        if (self.kill_type == npc.species):
            self.kill_total += 1

        if (self.kill == self.kill_total):
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message=Message('Quest ' + self.title + ' completed!', COLORS.get('success_text'))))
            pubsub.pubsub.unsubscribe_entity(self)

            self.completed = True
            if (self.return_to_quest_giver):
                self.owner.return_to_giver()

        return results

    def start_quest(self, game_map):
        global active_quests

        self.started = True
        active_quests.append(self)

        if (self.start_func):
            self.start_func(game_map)

        if (self.kill > 0):
            pubsub.pubsub.subscribe(pubsub.Subscription(self, pubsub.PubSubTypes.DEATH, kill_quest_npc_death))

        if self.kill_type:
            entities = game_map.current_level.find_entities_of_type(self.kill_type)

            if len(entities) < self.kill:
                gen = self.kill - len(entities)
                for _ in range(gen):
                    entity = bestiary.generate_entity(self.kill_type, game_map.dungeon_level)
                    avoid = entity.movement.routing_avoid
                    avoid.append(RoutingOptions.AVOID_FOV)
                    point = game_map.current_level.find_random_open_position(avoid)
                    entity.set_point(point)
                    game_map.current_level.add_entity(entity)

    def finish_quest(self):
        global active_quests

        active_quests.remove(self)

    def status(self):
        message = self.title
        if (self.kill_type):
            message += f': {str(self.kill_total)} of {str(self.kill)} {SPECIES_STRINGS[self.kill_type]} killed'

        return Message(message, COLORS.get('success_text'))
