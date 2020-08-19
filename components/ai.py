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
     Attack,
     CastSpell,
     Disolve,
     DoNothing,
     Envelop,
     Heal,
     MoveTowardsPointInNamespace,
     MoveTowardsTargetEntity,
     PickUp,
     PointToTarget,
     SeekTowardsLInfinityRadius,
     Skitter,
     SpawnEntity,
     Swarm,
     TravelToRandomPosition,)
from components.behaviour_trees.conditions import (
    ChangeAI,
    CheckHealthStatus,
    CoinFlip,
    FindEntities,
    FindNearestTargetEntity,
    InNamespace,
    IsAdjacent,
    IsCorpseInSpot,
    IsFinished,
    IsItemInSpot,
    IsNPCAdjacent,
    IsNPCInSpot,
    IsNPCParalyzed,
    NumberOfEntities,
    OtherEntityInSameSpot,
    OutsideL2Radius,
    SetNamespace,
    TargetWithinRange,
    WithinL2Radius,
    WithinPlayerFov,
    WithinRadius,)

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

class BasicNPC(BaseAI):
    """Simple NPC AI that acts as the default for most NPCs.

    This entity will attempt to do one of the following:
    1. If the entity's target is adjacent, attack
    2. If the entity's target is within range of the entity's weapon, attack
    3. If withing the player's FOV, move towards the player
    4. If a target point is set, move towards it
    5. Travel to a random empty tile

    """
    def __init__(self):
        self.tree = Root(
            Selection(
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
                Sequence(
                    InNamespace(name="target"),
                    TargetWithinRange(),
                    Attack()
                ),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity()),
                Sequence(
                    InNamespace(name="target_point"),
                    MoveTowardsPointInNamespace(name="target_point")),
                TravelToRandomPosition()
            )
        )

class ArcherNPC(BaseAI):
    """This AI presumes that the entity is armed with a ranged weapon. This
    means they will try and stay out of reach of their target and attack at
    range.

    This entity will attempt to do one of the following:
    1. If too close to the target, move away
    2. If the entity's target is within range of the entity's weapon, attack
    3. If not within range of the target, move towards the target
    4. If a target point is set, move towards it
    5. Pick a random empty tile and start travelling towards it
    
    """
    def __init__(self, radius=3):
        self.tree = Root(
            Selection(
                Sequence(
                    InNamespace(name="target"),
                    WithinRadius(radius=radius),
                    SeekTowardsLInfinityRadius(radius=radius)
                ),
                Sequence(
                    InNamespace(name="target"),
                    TargetWithinRange(),
                    Attack()
                ),
                Sequence(
                    InNamespace(name="target"),
                    MoveTowardsTargetEntity()
                ),
                Sequence(
                    InNamespace(name="target_point"),
                    MoveTowardsPointInNamespace(name="target_point")),
                TravelToRandomPosition()
            )
        )

class CaptainNPC(BaseAI):
    """AI for an entity that will spawn creatures to fill out a squad and then
    pitch in themselves.

    The captain will stay in the one spot until the player comes into view and
    will then attack. Until then it will spawn NPCs.

    This is meant for use with the barrcks prefab.

    """
    def __init__(self, spawn, min_time=5, max_time=10):
        number_of_turns = randint(min_time, max_time)
        self.tree = Root(
            Selection(
                Sequence(
                    SpawnEntity(spawn, min_time=min_time, max_time=max_time)
                ),
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
                Sequence(
                    WithinPlayerFov(),
                    MoveTowardsTargetEntity()
                ),
            )
        )

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
                            IsNPCParalyzed(),
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

class ConfusedNPC(BaseAI):
    """A confused NPC.

    Will randomly wander and attack random entities
    """
    def __init__(self, previous_ai, number_of_turns=10):
        self.number_of_turns = number_of_turns
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

class FrozenNPC(BaseAI):
    """AI for a frozen NPC.

    Always passes the turn without acting.
    """
    def __init__(self):
        self.tree = Root(DoNothing())

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

class HealerNPC(BaseAI):
    """AI for an entity that will heal other entities.

    This entity will attempt to do one of the following:
    1. Heal most injured entity in range
    2. If within the player's FOV stay heal radius away
    3. If the entity's target is adjacent, attack
    4. Follow another entity of the same species that moved last turn
    5. move to a random empty square

    Parameters
    ----------
    species: etc.enum.Species
        Species that this entity will attempt to heal.
    radius:
        The range that this entity will heal at.
    """
    def __init__(self, species=None, radius=3):
        self.tree = Root(
            Selection(
                Sequence(
                    FindEntities(species=species, radius=radius),
                    InNamespace(name="entities"),
                    Heal()
                ),
                Sequence(
                    WithinPlayerFov(),
                    WithinRadius(radius=radius),
                    SeekTowardsLInfinityRadius(radius=radius)
                ),
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
                Swarm(species=species),
                Skitter()
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

class NecromancerNPC(BaseAI):
    """AI for a necromancer.

    Necromancers attempt to always stay at exactly a given radius of the
    target.  If they fall within the radius, they will move away, if they fall
    outside the radius, they will move towards.  When they are at exactly the
    desired radius, they will spawn a zombie with a certain probability.
    """

    def __init__(self, radius=3):
        self.tree = Root(
            Selection(
                Sequence(
                    WithinPlayerFov(),
                    WithinRadius(radius=radius),
                    SeekTowardsLInfinityRadius(radius=radius)
                ),
                Sequence(
                    Negate(NumberOfEntities(radius=2, species=Species.UNDEAD, number_of_entities=4)),
                    CoinFlip(p=0.3),
                    SpawnEntity(bestiary.generate_random_zombie, min_time=0, max_time=0),
                ),
                Sequence(
                    InNamespace(name="target"),
                    IsAdjacent(),
                    Attack()
                ),
                Sequence(
                    InNamespace(name="target"),
                    WithinPlayerFov(),
                    CastSpell(spell=tome.magic_missile)
                ),
                DoNothing()
            )
        )

class PredatorNPC(BaseAI):
    """An entity which hunts other entity of a given species.

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
                    FindNearestTargetEntity(species=self.target_species),
                    MoveTowardsTargetEntity(),
                ),
                TravelToRandomPosition()))

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

class SpawningNPC(BaseAI):
    """AI for an entity that spawns another entity and does nothing else.

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
                )
            )

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
                    FindNearestTargetEntity(species=species, radius=move_towards_radius),
                    MoveTowardsTargetEntity(),
                ),
                Swarm(species=Species.ZOMBIE),
                Skitter()))
