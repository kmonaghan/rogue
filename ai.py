import libtcodpy as libtcod
import baseclasses
import pc
import messageconsole
import tome

class BasicMonster:
    #AI for a basic monster.
    def take_turn(self):
        #a basic monster takes its turn. if you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(baseclasses.fov_map, monster.x, monster.y):

            #move towards player if far away
            if monster.distance_to(pc.player) >= 2:
                monster.move_astar(pc.player)

            #close enough, attack! (if the player is still alive.)
            elif pc.player.fighter.hp > 0:
                monster.fighter.attack(pc.player)

class WanderingMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, rooms, old_ai):
        self.rooms = rooms
        self.old_ai = old_ai
        self.next_target()

    #AI for a basic monster.
    def take_turn(self):
        #a basic monster takes its turn. if you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(baseclasses.fov_map, monster.x, monster.y):
            self.owner.ai = self.old_ai

        else:
            if (monster.x == self.target.x) and (monster.y == self.target.y):
                self.next_target()

            monster.move_astar(self.target)

    def next_target(self):
        room = self.rooms.pop(0)
        self.target = baseclasses.Point(room[0], room[1])
        self.rooms.append(room)

class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while).
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
