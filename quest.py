import libtcodpy as libtcod
import game_state
import messageconsole
import screenrendering

def check_quests_for_npc_death(npc):
    for quest in game_state.active_quests:
        quest.kill_count(npc)

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

        print "Killed " + npc.name

        if (self.kill == self.kill_total):
            print "Completed kill " + npc.name
            messageconsole.message('Quest ' + self.title + ' completed!', libtcod.gold)
            self.completed = True
            if (self.return_to_quest_giver):
                print "return to owner"
                self.owner.return_to_giver()
            else:
                pc.player.completed_quest(self)
