import libtcodpy as libtcod
import baseclasses
import pc
import messageconsole
import tome

class BasicNPC:
    #AI for a basic npc.
    def take_turn(self):
        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(baseclasses.fov_map, npc.x, npc.y):

            #move towards player if far away
            if npc.distance_to(pc.player) >= 2:
                npc.move_astar(pc.player)

            #close enough, attack! (if the player is still alive.)
            elif pc.player.fighter.hp > 0:
                npc.fighter.attack(pc.player)

class WanderingNPC:
    #AI for a temporarily confused npc (reverts to previous AI after a while).
    def __init__(self, rooms, old_ai):
        self.rooms = rooms
        self.old_ai = old_ai
        self.next_target()

    #AI for a basic npc.
    def take_turn(self):
        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(baseclasses.fov_map, npc.x, npc.y):
            self.owner.ai = self.old_ai

        else:
            if (npc.x == self.target.x) and (npc.y == self.target.y):
                self.next_target()

            npc.move_astar(self.target)

    def next_target(self):
        room = self.rooms.pop(0)
        self.target = baseclasses.Point(room[0], room[1])
        self.rooms.append(room)

class ConfusedNPC:
    #AI for a temporarily confused npc (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=tome.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            messageconsole.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

class WarlordNPC:
    def __init__(self):
        self.summoned_goblins = False

    def take_turn(self):
        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(baseclasses.fov_map, npc.x, npc.y):

            if (self.summoned_goblins == False):
                self.summoned_goblins = True
                tome.cast_summon_goblin(npc)

            #move towards player if far away
            if npc.distance_to(pc.player) >= 2:
                npc.move_astar(pc.player)

            #close enough, attack! (if the player is still alive.)
            elif pc.player.fighter.hp > 0:
                npc.fighter.attack(pc.player)
