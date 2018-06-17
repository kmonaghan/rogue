import libtcodpy as libtcod

import game_state

from game_messages import Message

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
        self.owner.char = "Q"
        self.owner.color = libtcod.blue
        self.owner.always_visible = False
        game_state.active_quests.remove(self.quest)
        self.quest = None

    def start_quest(self):
        self.owner.char = "!"
        self.owner.color = libtcod.silver

    def return_to_giver(self):
        self.owner.color = libtcod.gold
        self.owner.always_visible = True

    def talk(self, pc):
        results = []
        if (self.quest == None):
            return results

        if (self.quest.started == False):
            results.append({'quest': self.quest})
        elif (self.quest.completed):
            self.completed_quest()

            results.append({'message': Message('Well done!', libtcod.white), 'xp': self.xp})
        else:
            results.append({'message': Message('Have you done it yet?', libtcod.white)})

        return results
