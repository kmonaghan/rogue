import tcod as libtcod

from game_messages import Message

import pubsub

class Questgiver:
    def __init__(self, quest = None):
        self.owner = None
        self.questchain = []
        self.quest = None
        if quest:
            self.add_quest(quest)

    def add_quest(self, quest):
        quest.owner = self
        self.questchain.append(quest)
        if (self.quest == None):
            self.quest = quest

    def completed_quest(self):
        results = []
        self.owner.char = "Q"
        self.owner.color = libtcod.blue
        self.owner.always_visible = False
        self.quest.finish_quest()

        self.quest = self.quest.next_quest

        if (self.quest):
            self.quest.owner = self
            self.owner.char = "?"
            self.owner.color = libtcod.gold
            results.append({'quest_onboarding': self.quest})

        return results

    def start_quest(self, game_map):
        self.owner.char = "!"
        self.owner.color = libtcod.silver
        self.quest.start_quest(game_map)

    def return_to_giver(self):
        self.owner.color = libtcod.gold
        self.owner.always_visible = True

    def talk(self, pc):
        results = []
        if not self.quest:
            return results

        if (self.quest.started == False):
            results.append({'quest_onboarding': self.quest})
        elif (self.quest.completed):
            pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('Well done!', libtcod.gold)))
            pubsub.pubsub.add_message(pubsub.Publish(self.quest, pubsub.PubSubTypes.EARNEDXP, target=pc))

            complete_result = self.completed_quest()

            results.extend(complete_result)
        else:
            results.append({'message': Message('Have you done it yet?', libtcod.white)})

        return results
