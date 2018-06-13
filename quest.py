import libtcodpy as libtcod
import game_state
import messageconsole
import screenrendering

def check_quests_for_npc_death(npc):
    for quest in game_state.active_quests:
        quest.kill_count(npc)

def kill_gobbos(kill = 5):
    title = "Kill Gobbos"
    description = "Get rid of them. I don't care how."

    q = Quest(title, description, 100)
    q.kill = kill
    q.kill_type = "goblin"
    q.return_to_quest_giver = True

    return q

def kill_orcs(kill = 5):
    title = "Kill Orcs"
    description = "Get rid of them. I don't care how."

    q = Quest(title, description, 200)
    q.kill = kill
    q.kill_type = "orc"
    q.return_to_quest_giver = True

    return q

def kill_trolls(kill = 5):
    title = "Kill Trolls"
    description = "Get rid of them. I don't care how."

    q = Quest(title, description, 300)
    q.kill = kill
    q.kill_type = "troll"
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

    def start_quest(self, pc):
        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = screenrendering.menu(self.title + "\n" + self.description,
                                            [['Accept Quest',libtcod.white],
                                            ['Reject Quest',libtcod.white]],
                                            screenrendering.LEVEL_SCREEN_WIDTH)

        if choice == 0:
            messageconsole.message('Quest ' + self.title + ' accepted!', libtcod.green)
            game_state.active_quests.append(self)
            self.started = True
            self.owner.start_quest()
        elif choice == 1:
            return

    def kill_count(self, npc):
        if (self.kill == 0):
            return

        if (self.kill_type == npc.name):
            self.kill_total = self.kill_total + 1

        if (self.kill == self.kill_total):
            messageconsole.message('Quest ' + self.title + ' completed!', libtcod.gold)
            self.completed = True
            if (self.return_to_quest_giver):
                self.owner.return_to_giver()
            else:
                game_state.player.completed_quest(self)
