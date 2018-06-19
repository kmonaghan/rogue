import libtcodpy as libtcod

import bestiary
import tome

from game_messages import Message

from map_objects.point import Point

class BasicNPC:
    #AI for a basic npc.
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):

            #move towards player if far away
            if npc.distance_to(target) >= 2:
                npc.move_astar(target, entities, game_map)

            #close enough, attack! (if the player is still alive.)
            elif target.fighter.hp > 0:
                attack_results = npc.fighter.attack(target)
                results.extend(attack_results)

        return results

class WanderingNPC:
    #AI for a temporarily confused npc (reverts to previous AI after a while).
    def __init__(self, rooms, old_ai):
        self.rooms = rooms
        self.old_ai = old_ai
        self.next_target()

    #AI for a basic npc.
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):
            self.owner.ai = self.old_ai

        else:
            if (npc.x == self.target.x) and (npc.y == self.target.y):
                self.next_target()

            npc.move_astar(self.target, entities, game_map)

        return results

    def next_target(self):
        room = self.rooms.pop(0)
        self.target = room.center()
        self.rooms.append(room)

class ConfusedNPC:
    #AI for a temporarily confused npc (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=10): #tome.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            messageconsole.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

        return results

class StrollingNPC:
    #AI for a temporarily confused npc (reverts to previous AI after a while).
    def __init__(self):
        self.moved = False

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if (self.moved == False):
            dx = libtcod.random_get_int(0, -1, 1)
            dy = libtcod.random_get_int(0, -1, 1)
            self.moved = self.owner.attempt_move(self.owner.x + dx, self.owner.y + dy, game_map, entities)
        else:
            self.moved = False

        return results

class WarlordNPC:
    def __init__(self):
        self.summoned_goblins = False
        self.summoned_orcs = False
        self.summoned_trolls = False

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):

            if (self.summoned_orcs == False) or (self.summoned_goblins == False) or (self.summoned_trolls == False):
                health = (npc.fighter.hp * 100.0) / npc.fighter.max_hp

                if (health < 40):
                    if (self.summoned_trolls == False):
                        self.summoned_trolls = True
                        results.append({'message': Message('Trolls! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.troll, game_map, entities, 2)

                        return results

                elif (health < 60):
                    if (self.summoned_orcs == False):
                        self.summoned_orcs = True
                        results.append({'message': Message('Orcs! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.orc, game_map, entities, 4)

                        return results

                elif (health < 80):
                    if (self.summoned_goblins == False):
                        self.summoned_goblins = True
                        results.append({'message': Message('Goblins! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.goblin, game_map, entities, 6)

                        return results

            #move towards player if far away
            if npc.distance_to(target) >= 2:
                npc.move_astar(target, entities, game_map)

            #close enough, attack! (if the player is still alive.)
            elif target.fighter.hp > 0:
                attack_results = npc.fighter.attack(target)
                results.extend(attack_results)

        return results
