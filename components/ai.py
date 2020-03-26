__metaclass__ = type

import bestiary
import tome
import pubsub

from random import randint

from game_messages import Message

from map_objects.point import Point

from etc.enum import HealthStates, ResultTypes, Species

from components.behaviour_trees.root import Root
from components.behaviour_trees.composite import (
    Selection, Sequence, Negate)
from components.behaviour_trees.leaf import (
     Attack, MoveTowardsTargetEntity, TravelToRandomPosition, SeekTowardsLInfinityRadius,
     MoveTowardsPointInNamespace, SpawnEntity, DoNothing, Skitter, Swarm, PointToTarget,
     PickUp, Disolve, Envelop)
from components.behaviour_trees.conditions import (
    IsAdjacent, IsFinished, IsItemInSpot, WithinPlayerFov, InNamespace, CoinFlip,
    FindNearestTargetEntity, WithinL2Radius, OtherEntityInSameSpot,
    OutsideL2Radius, CheckHealthStatus, SetNamespace, NumberOfEntities,
    IsNPCInSpot, IsCorpseInSpot, IsNPCAdjacent, IsNPCAParalyzed)

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
        current_target = self.tree.namespace.get("target")

        if current_target == target:
            return

        self.tree.namespace["target"] = target
        pubsub.pubsub.subscribe(pubsub.Subscription(self.owner, pubsub.PubSubTypes.DEATH, pubsub.on_entity_death))

    def remove_target(self, target=None):
        current_target = self.tree.namespace.get("target")
        if current_target and current_target.uuid == target.uuid:
            del self.tree.namespace["target"]

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
                    MoveTowardsTargetEntity()),
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
                    MoveTowardsTargetEntity()),
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
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity()),
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
                    Negate(NumberOfEntities(radius=2, species=Species.UNDEAD, number_of_entities=4)),
                    CoinFlip(p=0.3),
                    SpawnEntity(bestiary.generate_random_zombie, min_time=0, max_time=0),
                ),
#                Sequence(
#                    #WithinL2Radius(radius=move_towards_radius),
#                    SeekTowardsLInfinityRadius(radius=seeking_radius)
#                ),
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
            )
        )

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
                    MoveTowardsTargetEntity()),
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
                    MoveTowardsTargetEntity()),
                TravelToRandomPosition()))

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
                    MoveTowardsTargetEntity()),
                Skitter()))

class ConfusedNPC(BaseAI):
    """A confused NPC.

    Will randomly wander and attack random entities
    """
    def __init__(self, previous_ai, number_of_turns=10):
        self.number_of_turns
        self.tree = Root(
            Selection(
                Sequence(
                    IsFinished(number_of_turns),
                    ChangeAI(previous_ai)
                ),
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Skitter()))

class SpawningNPC(BaseAI):
    """AI for an entity that spawns another entity.

    Parameters
    ----------
    spawn: method
        The method to generate the spawned entity.
    min_time: int
        Mininum number of turns before attempting to spawn.
        Default: 5
    max_time: int
        Maximium number of turns before spawning.
        Default: 10
    """
    def __init__(self, spawn=None, min_time = 5, max_time = 10):
        self.tree = Root(
            Selection(
                Sequence(
                    SpawnEntity(spawn, min_time=min_time, max_time=max_time)),
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
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    InNamespace(name="target"),
                    MoveTowardsTargetEntity()),
                Sequence(
                    FindNearestTargetEntity(range=2,species_type=self.target_species),
                    MoveTowardsTargetEntity(),
                ),
                TravelToRandomPosition()))

class HatchingNPC(BaseAI):
    """AI for an entity that turns into another entity.

    Parameters
    ----------
    spawn: method
        The method to generate the spawned entity.
    min_time: int
        Mininum number of turns before attempting to spawn.
        Default: 5
    max_time: int
        Maximium number of turns before spawning.
        Default: 10
    """
    def __init__(self, spawn, min_time=5, max_time=10):
        number_of_turns = randint(min_time, max_time)
        self.tree = Root(
            Selection(
                Sequence(
                    IsFinished(number_of_turns),
                    SpawnEntity(spawn, hatch=True)
                )))

class CaptainNPC(BaseAI):
    """AI for a .

    The captain will stay in the one spot unti the payer comes into view and will
    then attack. Until then it will spawn NPCs.

    This is meant for use with the brrcks prefab.

    """
    def __init__(self, spawn, min_time=5, max_time=10):
        number_of_turns = randint(min_time, max_time)
        self.tree = Root(
            Selection(
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity()
                ),
                Sequence(
                    SpawnEntity(spawn, min_time=min_time, max_time=max_time)
                ),
            )
        )

class WarlordNPC(BaseAI):
    """AI for a warlord.

    The warlord will stay in the one spot unti the payer comes into view and will
    then attack.

    When injured, will summon 2 minions to help, scaling with the amount of
    damage taken.
    Injured: Goblins
    Badly injured: Orcs
    Near death: Trolls

    """
    def __init__(self):
        self.tree = Root(
            Selection(
                Sequence(
                    Negate(InNamespace(name="summoned_goblins")),
                    CheckHealthStatus(HealthStates.INJURED),
                    SpawnEntity(bestiary.goblin, min_time=0, max_time=0),
                    SpawnEntity(bestiary.goblin, min_time=0, max_time=0),
                    SetNamespace(name="summoned_goblins")
                ),
                Sequence(
                    Negate(InNamespace(name="summoned_orcs")),
                    CheckHealthStatus(HealthStates.BADLY_INJURED),
                    SpawnEntity(bestiary.orc, min_time=0, max_time=0),
                    SpawnEntity(bestiary.orc, min_time=0, max_time=0),
                    SetNamespace(name="summoned_orcs")
                ),
                Sequence(
                    Negate(InNamespace(name="summoned_trolls")),
                    CheckHealthStatus(HealthStates.NEAR_DEATH),
                    SpawnEntity(bestiary.troll, min_time=0, max_time=0),
                    SpawnEntity(bestiary.troll, min_time=0, max_time=0),
                    SetNamespace(name="summoned_trolls")
                ),
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity()
                )
            )
        )

class ZombieNPC(BaseAI):
    """Rwarrr...."""
    def __init__(self, move_towards_radius=6, species=Species.NONDESCRIPT):
        self.tree = Root(
            Selection(
                Sequence(
                    IsAdjacent(),
                    Attack()),
                Sequence(
                    WithinL2Radius(radius=move_towards_radius),
                    MoveTowardsTargetEntity()),
                Sequence(
                    FindNearestTargetEntity(range=move_towards_radius,species_type=species),
                    MoveTowardsTargetEntity(),
                ),
                Swarm(species=species),
                Skitter()))

class CleanerNPC(BaseAI):
    def __init__(self):
        self.tree = Root(
            Selection(
                Sequence( #Do something to entity in spot
                    OtherEntityInSameSpot(),
                    Selection(
                        Sequence(
                            IsItemInSpot(),
                            PickUp()
                        ),
                        Sequence(
                            IsCorpseInSpot(),
                            Disolve()
                        ),
                        Sequence(
                            IsNPCInSpot(),
                            Attack()
                        ),
                    ),
                ),
                Sequence( #Do something to entity adject
                    IsNPCAdjacent(),
                    Selection(
                        Sequence(
                            IsNPCAParalyzed(),
                            Envelop()
                        ),
                        Sequence(
                            InNamespace(name="target"),
                            IsAdjacent(),
                            Attack()
                        ),
                    )
                ),
                Sequence( #Shuffle along
                    Skitter()
                )
            ))
