import libtcodpy as libtcod
import messageconsole
import screenrendering

def asdadasd():
    print "asdasd"

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
            pc.add_quest(self)
            self.started = True
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
            if (self.return_to_quest_giver == False):
                self.owner.complete_quest(self)
