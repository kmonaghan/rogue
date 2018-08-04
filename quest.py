import libtcodpy as libtcod

import game_state
from random import choice

from game_messages import Message
from species import Species

def check_quests_for_npc_death(npc):
    results = []
    for quest in game_state.active_quests:
        results.append(quest.kill_count(npc))

    return results

def kill_vermin(kill = 10):
    title = "Kill Vermin"
    description = "These caves are riddled with rats and snakes. Clear them out."

    q = Quest(title, description, 100)
    q.kill = kill
    q.kill_type = Species.RAT
    q.return_to_quest_giver = True

    return q

def kill_gobbos(kill = 5):
    title = "Kill Gobbos"
    description = "Get rid of them. I don't care how."

    q = Quest(title, description, 100)
    q.kill = kill
    q.kill_type = Species.GOBLIN
    q.return_to_quest_giver = True

    return q

def kill_orcs(kill = 5):
    title = "Kill Orcs"
    description = "Get rid of them. I don't care how."

    q = Quest(title, description, 200)
    q.kill = kill
    q.kill_type = Species.ORC
    q.return_to_quest_giver = True

    return q

def kill_trolls(kill = 5):
    title = "Kill Trolls"
    description = "Get rid of them. I don't care how."

    q = Quest(title, description, 300)
    q.kill = kill
    q.kill_type = Species.TROLL
    q.return_to_quest_giver = True

    return q

def kill_warlord():
    title = "Kill the Warlord"
    description = "Time to take down the king of the hill. Or dungeon as it is in this case."

    q = Quest(title, description, 500)
    q.kill = 1
    q.kill_type = "warlord"
    q.return_to_quest_giver = True

    return q

class Quest:
    def __init__(self, title, description, xp, kill=0, kill_type=None):
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
        self.npc = None

    def kill_count(self, npc):
        results = []

        ##print "tsting kill condition: " + npc.name
        if (self.kill == 0):
            return

        if (self.kill_type == npc.species):
            ##print "add a kill"
            self.kill_total += 1

        if (self.kill == self.kill_total):
            #print "quest complete"
            results.append({'message': Message('Quest ' + self.title + ' completed!', libtcod.gold)})
            self.completed = True
            if (self.return_to_quest_giver):
                self.owner.return_to_giver()

        return results

    def start_quest(self, game_map):
        self.started = True
        game_state.active_quests.append(self)

        if (self.npc):
            room = choice(game_map.rooms)
            aPoint = room.center()
            self.npc.x = aPoint.x
            self.npc.y = aPoint.y
            game_map.add_npc_to_map(self.npc)
