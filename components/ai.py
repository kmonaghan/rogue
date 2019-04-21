__metaclass__ = type

import tcod as libtcod

import bestiary
import tome

from random import randint

from game_messages import Message

from map_objects.point import Point

from etc.enum import ResultTypes, Species

from components.behaviour_trees.root import Root
from components.behaviour_trees.composite import (
    Selection, Sequence, Negate)
from components.behaviour_trees.leaf import (
     Attack, MoveTowardsTargetEntity, TravelToRandomPosition,
     MoveTowardsPointInNamespace, SpawnEntity, DoNothing, Skitter, PointToTarget)
from components.behaviour_trees.conditions import (
    IsAdjacent, WithinPlayerFov, InNamespace, CoinFlip, FindNearestTargetEntity,
    OutsideL2Radius)

class BaseAI:
    """Base class for NPC AI.

    NPC's behaviour is defined by a behaviour tree, stored in the tree
    attribute.  Behaviour trees have a tick method, which is called when the
    reature takes a turn.  The tick method returns a turn result dictionary
    that summarizes the turn's effect on the game state.
    """
    def take_turn(self, game_map):
        _, results = self.tree.tick(self.owner, game_map)
        return results

    def set_target(self, target):
        self.tree.namespace["target"] = target

class PatrollingNPC(BaseAI):
    """Simple NPC ai.

    When in the targets POV, attempt to move towards the target.  If adjacent
    to the target, attack.
    """
    def __init__(self):
        self.tree = Root(
            Selection(
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity(target_point_name="target_point")),
                Sequence(
                    InNamespace(name="target_point"),
                    MoveTowardsPointInNamespace(name="target_point")),
                TravelToRandomPosition()))

class TetheredNPC(BaseAI):
    """Simple NPC ai.

    """
    def __init__(self, radius=4, tether_point=None):
        self.tree = Root(
            Selection(
                Sequence(
                    PointToTarget(tether_point, "radius_point"),
                    OutsideL2Radius(radius),
                    MoveTowardsPointInNamespace(name="radius_point")
                ),
                Skitter()))

class BasicNPC(BaseAI):
    """Simple NPC ai.

    When in the targets POV, attempt to move towards the target.  If adjacent
    to the target, attack.
    """
    def __init__(self):
        self.tree = Root(
            Selection(
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity(target_point_name="target_point")),
                Sequence(
                    InNamespace(name="target_point"),
                    MoveTowardsPointInNamespace(name="target_point")),
                TravelToRandomPosition()))

class GuardNPC(BaseAI):
    """An ai for a NPC which guards a point.

    If adjacent to the target, attack.
    When in the targets POV, and inside the guard radius, attempt to move
    towards the target.
    When outside the guard radius, return to radius
    Move randomly within guard radius
    """
    def __init__(self, radius=4, guard_point=None):
        self.radius = radius

        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity(target_point_name="target_point")),
                Sequence(
                    PointToTarget(guard_point, "radius_point"),
                    OutsideL2Radius(self.radius),
                    MoveTowardsPointInNamespace(name="radius_point")
                ),
                Skitter()))

class FrozenNPC(BaseAI):
    """AI for a frozen NPC.

    Always passes the turn without acting.
    """
    def __init__(self):
        self.tree = Root(DoNothing())


class NecromancerNPC(BaseAI):
    """AI for a necromancer.

    Necromancers attempt to always stay at exactly a given radius of the
    target.  If they fall within the radius, they will move away, if they fall
    outside the radius, they will move towards.  When they are at exactly the
    desired radius, they will spawn a zombie with a certain probability.
    """
    def __init__(self, move_towards_radius=6, seeking_radius=3):
        self.tree = Root(
            Selection(
                Sequence(
                    AtLInfinityRadius(radius=seeking_radius),
                    CoinFlip(p=0.3),
                    #SpawnEntity(game_objects.monsters.Zombie)
                    ),
                Sequence(
                    WithinL2Radius(radius=move_towards_radius),
                    SeekTowardsLInfinityRadius(radius=seeking_radius)),
                TravelToRandomPosition()))

class HunterNPC(BaseAI):
    def __init__(self, sensing_range=12):
        self.sensing_range = sensing_range
        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinL2Radius(radius=sensing_range),
                    MoveTowardsTargetEntity(target_point_name="target_point")),
                TravelToRandomPosition()))

class HuntingNPC(BaseAI):
    """A more dangerous monster.

    Attempts to move towards the target even if not in the targets POV.
    """
    def __init__(self, sensing_range=12):
        self.sensing_range = sensing_range
        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinL2Radius(radius=sensing_range),
                    MoveTowardsTargetEntity(target_point_name="target_point")),
                TravelToRandomPosition()))


class ZombieNPC(BaseAI):
    """Similar to a HuntingNPC, but will not wander."""
    def __init__(self, move_towards_radius=6):
        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinL2Radius(radius=move_towards_radius),
                    MoveTowardsTargetEntity(target_point_name="target_point"))))


class SkitteringNPC(BaseAI):
    """An impatient NPC.

    When close by, attempts to move towards the target.  Otherwise, moves to a
    random adjacent square.
    """
    def __init__(self, skittering_range=3):
        self.skittering_range = skittering_range
        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinL2Radius(radius=skittering_range),
                    MoveTowardsTargetEntity(target_point_name="target_point")),
                Skitter()))

class ConfusedNPC(BaseAI):
    """A confused NPC.

    Will randomly wander and attack random entities
    """
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.tree = Root(
            Selection(
                Sequence(
                    IsFinished(number_of_turns),
                    ChangeAI(self.previous_ai)
                ),
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Skitter()))

class SpawningNPC(BaseAI):
    """AI for an entity that spawns other entities.

    """
    def __init__(self, spawn=None):
        self.spawn = spawn
        self.tree = Root(
            Selection(
                Sequence(
                    CoinFlip(),
                    SpawnEntity(spawn)),
                DoNothing()))

class PredatorNPC(BaseAI):
    """A NPC which hunts other NPCs.

    Will randomly wander until it encounters a NPC of the correct type
    """
    def __init__(self, species=Species.NONDESCRIPT):

        self.target_species= species

        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    FindNearestTargetEntity(range=2,species_type=self.target_species),
                    MoveTowardsTargetEntity(target_point_name="target_point"),
                ),
                TravelToRandomPosition()))

class WarlordNPC:
    def __init__(self):
        self.summoned_goblins = False
        self.summoned_orcs = False
        self.summoned_trolls = False

    def take_turn(self, game_map):
        results = []
        #a basic npc takes its turn. if you can see it, it can see you
        npc = self.owner
        if game_map.current_level.fov[npc.x, npc.y]:

            if (self.summoned_orcs == False) or (self.summoned_goblins == False) or (self.summoned_trolls == False):
                health = (npc.health.hp * 100.0) / npc.health.max_hp

                if (health < 40):
                    if (self.summoned_trolls == False):
                        self.summoned_trolls = True
                        results.append({ResultTypes.MESSAGE: Message('Trolls! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.troll, game_map, 2)

                        return results

                elif (health < 60):
                    if (self.summoned_orcs == False):
                        self.summoned_orcs = True
                        results.append({ResultTypes.MESSAGE: Message('Orcs! To me!', libtcod.red)})
                        tome.cast_summon_npc(Point(npc.x, npc.y), bestiary.orc, game_map, 4)

                        return results

                elif (health < 80):
                    if (self.summoned_goblins == False):
                        self.summoned_goblins = True
                        results.append({ResultTypes.MESSAGE: Message('Goblins! To me!', libtcod.red)})
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

    def take_turn(self, game_map):
        results = []

        npc = self.owner
        if game_map.current_level.fov[npc.x, npc.y]:
            if not self.ritual_started:
                self.ritual_started = True

        if self.ritual_started and (self.ritual_turns > 0):
             self.ritual_turns -= 1

        if not self.ritual_cast and (self.ritual_turns == 0):
            tome.resurrect_all_npc(bestiary.reanmimate, game_map, target)
            results.append({ResultTypes.MESSAGE: Message('Rise and serve me again, now and forever!', libtcod.red)})
            self.ritual_cast = True

        return results

class Hatching:
    def __init__(self, hatches):
        self.incubate = randint(5, 15)
        self.hatches = hatches

    def take_turn(self, game_map):
        results = []

        self.incubate -= 1

        if (self.incubate < 1):
            npc = self.owner

            game_map.current_level.remove_entity(npc)
            self.hatches.x = npc.x
            self.hatches.y = npc.y
            game_map.current_level.add_entity(self.hatches)

        return results
