__metaclass__ = type

import tcod as libtcod

import bestiary
import tome

from random import randint

from game_messages import Message

from map_objects.point import Point

class BasicNPC:
    #AI for a basic npc.
    def take_turn(self, target, fov_map, game_map):
        results = []

        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):

            #move towards player if far away
            if npc.point.distance_to(target.point) >= 2:
                npc.movement.move_astar(target, game_map)

            #close enough, attack! (if the player is still alive.)
            elif target.health.hp > 0:
                attack_results = npc.offence.attack(target)
                results.extend(attack_results)

        return results

class PatrollingNPC:
    def __init__(self, rooms, old_ai):
        self.rooms = rooms
        self.old_ai = old_ai
        self.next_target()

    #AI for a basic npc.
    def take_turn(self, target, fov_map, game_map):
        results = []

        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):
            self.owner.ai = self.old_ai

        else:
            if (npc.x == self.target.x) and (npc.y == self.target.y):
                self.next_target()

            npc.movement.move_astar(self.target, game_map)

        return results

    def next_target(self):
        room = self.rooms.pop(0)
        self.target = room.center()
        self.rooms.append(room)

class ConfusedNPC:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map):
        results = []

        if self.number_of_turns > 0:
            dx = libtcod.random_get_int(0, -1, 1)
            dy = libtcod.random_get_int(0, -1, 1)

            self.owner.movement.attempt_move(Point(self.owner.x + dx, self.owner.y + dy), game_map)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), libtcod.red)})

        return results

class StrollingNPC:
    def __init__(self, attacked_ai = None, tethered = None, tethered_distance = 4, aggressive = False, pursue_distance = 10):
        self.moved = False
        self.attacked_ai = attacked_ai
        self.tethered = tethered
        self.tethered_distance = tethered_distance
        self.aggressive = aggressive
        self.pursue_distance = pursue_distance

    def take_turn(self, target, fov_map, game_map):
        results = []

        if (self.aggressive and libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y)):
            #move towards player if far away
            distance = self.owner.point.distance_to(target.point)
            if distance > self.pursue_distance:
                print("returning to patrol point")
                self.owner.movement.move_towards(self.tethered, game_map)
                return results
            elif distance >= 2:
                self.owner.movement.move_astar(target, game_map)
                self.moved = True
            #close enough, attack! (if the player is still alive.)
            elif target.health.hp > 0:
                attack_results = self.owner.offence.attack(target)
                results.extend(attack_results)
                self.moved = True

        if not self.moved:
            if self.tethered:
                if (self.owner.point.distance_to(self.tethered) > self.tethered_distance):
                    #print("too far from tethered point: " + self.tethered.describe())
                    self.owner.movement.move_towards(self.tethered, game_map)
                    return results

            dx = libtcod.random_get_int(0, -1, 1)
            dy = libtcod.random_get_int(0, -1, 1)
            self.moved = self.owner.movement.attempt_move(Point(self.owner.x + dx, self.owner.y + dy), game_map)
        else:
            self.moved = False

        return results

class WarlordNPC:
    def __init__(self):
        self.summoned_goblins = False
        self.summoned_orcs = False
        self.summoned_trolls = False

    def take_turn(self, target, fov_map, game_map):
        results = []
        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):

            if (self.summoned_orcs == False) or (self.summoned_goblins == False) or (self.summoned_trolls == False):
                health = (npc.health.hp * 100.0) / npc.health.max_hp

                if (health < 40):
                    if (self.summoned_trolls == False):
                        self.summoned_trolls = True
                        results.append({'message': Message('Trolls! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.troll, game_map, 2)

                        return results

                elif (health < 60):
                    if (self.summoned_orcs == False):
                        self.summoned_orcs = True
                        results.append({'message': Message('Orcs! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.orc, game_map, 4)

                        return results

                elif (health < 80):
                    if (self.summoned_goblins == False):
                        self.summoned_goblins = True
                        results.append({'message': Message('Goblins! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.goblin, game_map, 6)

                        return results

            #move towards player if far away
            if npc.point.distance_to(target.point) >= 2:
                npc.movement.move_astar(target, game_map)

            #close enough, attack! (if the player is still alive.)
            elif target.health.hp > 0:
                attack_results = npc.attack.attack(target)
                results.extend(attack_results)

        return results

class NecromancerNPC:
    def __init__(self):
        self.ritual_cast = False
        self.ritual_started = False
        self.ritual_turns = 50

    def take_turn(self, target, fov_map, game_map):
        results = []

        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):
            if not self.ritual_started:
                self.ritual_started = True

        if self.ritual_started and (self.ritual_turns > 0):
             self.ritual_turns -= 1

        if not self.ritual_cast and (self.ritual_turns == 0):
            tome.resurrect_all_npc(bestiary.reanmimate, game_map, target)
            results.append({'message': Message('Rise and serve me again, now and forever!', libtcod.red)})
            self.ritual_cast = True

        return results

class Hunter(StrollingNPC):
    def __init__(self, attacked_ai = None, hunting = None):
        super(Hunter, self).__init__(attacked_ai = attacked_ai)
        self.hunting = hunting

    def take_turn(self, target, fov_map, game_map):
        results = []

        npc = self.owner

        target = game_map.find_closest(Point(npc.x, npc.y), self.hunting)

        if (target):
            dist = max(abs(target.x - npc.x), abs(target.y - npc.y))

            if dist > 1:
                npc.movement.move_astar(target, game_map)
                return results
            elif not target.health.dead and (dist == 1):
                attack_results = npc.offence.attack(target)
                dead_entity = None
                for turn_result in attack_results:
                    dead_entity = turn_result.get('dead')

                if (dead_entity):
                    results.append({'entity_dead': target, 'killer': npc})

                return results

        return super(Hunter, self).take_turn(target, fov_map, game_map)

class Hatching:
    def __init__(self, hatches):
        self.incubate = randint(5, 15)
        self.hatches = hatches

    def take_turn(self, target, fov_map, game_map):
        results = []

        self.incubate -= 1

        if (self.incubate < 1):
            npc = self.owner

            game_map.remove_entity_from_map(npc)
            self.hatches.x = npc.x
            self.hatches.y = npc.y
            game_map.add_entity_to_map(self.hatches)

        return results

class SpawnNPC:
    def __init__(self, spawn):
        self.spawn = spawn
        self.turns_since_last_spawn = 0

    def take_turn(self, target, fov_map, game_map):
        results = []

        if ((randint(0, 10) + self.turns_since_last_spawn) > 18):
            npc = self.spawn(self.owner.point)
            if (game_map.find_closest(self.owner.point, npc.species, 1) == None):
                self.turns_since_last_spawn = 0
                game_map.add_entity_to_map(npc)
                #print("Spawned " + npc.name)
            else:
                #print("Already " + npc.name + " nearby")
                pass
        else:
            self.turns_since_last_spawn += 1

        return results

class ScreamerNPC:
    def __init__(self, alert_npc_type, alert_range = 1):
        self.alert_npc_type = alert_npc_type
        self.alert_range = alert_range

    def take_turn(self, target, fov_map, game_map):
        results = []

        npcs = game_map.find_all_closest(self.owner.point, self.alert_npc_type, self.alert_range)

        if len(npcs):
            for npc in npcs:
                npc.add_component(BasicNPC(), "ai")

            results.append({'message': Message('Alert nearby creatures!', libtcod.red)})

        return results
