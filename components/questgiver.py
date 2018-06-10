import libtcodpy as libtcod

import game_state
import messageconsole

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
        if (self.quest == None):
            return

        if (self.quest.started == False):
            self.quest.start_quest(pc)
        elif (self.quest.completed):
            messageconsole.message('Well done!')
            messageconsole.message('You have earned ' + str(self.quest.xp) + 'XP')
            pc.completed_quest(self.quest)
            self.completed_quest()
        else:
            messageconsole.message('Have you done it yet?')

    def change_state(Self):
            npc.char = '!'
            npc.color = libtcod.silver
