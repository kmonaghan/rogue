import libtcodpy as libtcod

import game_state
from random import choice

from game_messages import Message
from species import Species

active_quests = []

def check_quests_for_npc_death(npc):
    global active_quests
    results = []
    for quest in active_quests:
        if (quest.kill > 0):
            results.append(quest.kill_count(npc))

    return results

def check_quest_for_location(point):
    global active_quests

    results = []

    for quest in active_quests:
        if (quest.map_point):
            if (point == quest.map_point):
                #TODO: do something with a location quest
                print("TODO: do something with a location quest")
                results.append({'message': Message('Quest completed!', libtcod.gold)})

    return results

def kill_vermin(kill = 10):
    title = "Kill Vermin"
    description = "These caves are riddled with rats and snakes. Clear them out."

    q = Quest(title, description, 100)
    q.kill = kill
    q.kill_type = Species.RAT
    q.return_to_quest_giver = True

    return q

def kill_rats_nests(kill = 3):
    title = "Kill Vermin"
    description = "These caves are riddled with rats. Get rid of thier nests."

    q = Quest(title, description, 100)
    q.kill = kill
    q.kill_type = Species.RATNEST
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
    def __init__(self, title, description, xp, kill=0, kill_type=None, start_func = None, map_point = None):
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
        self.start_func = start_func
        self.map_point = map_point

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
        global active_quests

        self.started = True
        active_quests.append(self)

        if (self.start_func):
            self.start_func()

        if (self.npc):
            room = choice(game_map.rooms)
            aPoint = room.center()
            self.npc.x = aPoint.x
            self.npc.y = aPoint.y
            game_map.add_entity_to_map(self.npc)

    def status(self):
        message = self.title
        if (self.kill_type):
            message += ' ' + str(self.kill_total) + ' of ' + str(self.kill) + ' killed'

        return Message(message, libtcod.gold)
