'''via https://github.com/madrury/roguelike
'''
import logging

from random import choice, randint, uniform

import tome

from components.behaviour_trees.root import Node

from etc.enum import TreeStates, ResultTypes

from map_objects.point import Point

from utils.pathfinding import get_path_to, move_to_radius_of_target
from utils.utils import random_walkable_position, random_adjacent

class Attack(Node):
    """The owner attackes the target."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        if not target:
            logging.info(f"No target - how did we get here?")
            return TreeStates.FAILURE, []

        if target.health.dead:
            #logging.info("Attack: FAILURE - target dead, removing")
            del self.namespace["target"]
            return TreeStates.FAILURE, []

        return (TreeStates.SUCCESS,
                    owner.offence.attack(target, game_map))

class CastSpell(Node):
    """The owner casts a spell the target."""
    def __init__(self, spell):
        self.spell = spell

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        if not target:
            logging.info(f"No target - how did we get here?")
            return TreeStates.FAILURE, []

        if target.health.dead:
            #logging.info("Attack: FAILURE - target dead, removing")
            del self.namespace["target"]
            return TreeStates.FAILURE, []

        return (TreeStates.SUCCESS,
                    self.spell(game_map=game_map,
                                caster=owner,
                                target=target))

class Disolve(Node):
    def tick(self, owner, game_map):
        super().tick(owner, game_map)

        target = self.namespace["corpse"]

        if target:
            del self.namespace["corpse"]
            if target.death.rotting_time > 1:
                target.death.rotting_time = min(1, target.death.rotting_time - 5)
                target.death.decompose(game_map)

            return TreeStates.SUCCESS, []

        return TreeStates.FAILURE, []

class DoNothing(Node):
    """Take no action and pass the turn."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        return TreeStates.SUCCESS, []

class Envelop(Node):
    def tick(self, owner, game_map):
        super().tick(owner, game_map)

        target = self.namespace["paralyzed"]

        if target:
            del self.namespace["paralyzed"]
            return TreeStates.SUCCESS, [{ResultTypes.SET_POSITION: (owner, target.point)}]

        return TreeStates.FAILURE, []

class Heal(Node):
    """Heal the most injured entity in a given list.

    The entity is healed for [casters level]d8 points.
    """
    def tick(self, owner, game_map):
        super().tick(owner, game_map)

        entities = self.namespace["entities"]

        if entities:
            entities.sort(key=lambda x: x.health.hp)
            self.namespace.pop("entities", None)

            if entities[0].health.hp < entities[0].health.max_hp:
                return (TreeStates.SUCCESS,
                            tome.heal(game_map=game_map,
                                        caster=owner,
                                        target=entities[0],
                                        number_of_dice=owner.level.current_level,
                                        type_of_dice=8))

        return TreeStates.FAILURE, []

class MoveTowardsTargetEntity(Node):
    """Move the owner towards a target and remember the target's point."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        if not target:
            return TreeStates.FAILURE, []

        self.namespace["path"] = get_path_to(game_map,
                                                (owner.x, owner.y),
                                                (target.x, target.y),
                                                routing_avoid=owner.movement.routing_avoid)
        if len(self.namespace["path"]) < 1:
            return TreeStates.SUCCESS, []
        results = [{
            ResultTypes.MOVE_WITH_PATH: (owner, self.namespace["path"])}]
        return TreeStates.SUCCESS, results

class MoveTowardsPointInNamespace(Node):

    def __init__(self, name):
        self.name = name

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        if not self.namespace.get(self.name):
            raise ValueError(f"{self.name} is not in tree namespace!")
        point = self.namespace.get(self.name)
        path = self.namespace.get("path")

        if path and len(path) > 1 and (Point(path[0][0], path[0][1]) == owner.point):
            path.pop(0)

            if not game_map.current_level.blocked[path[0][0], path[0][1]]:
                return TreeStates.SUCCESS, [{ResultTypes.MOVE_WITH_PATH: (owner, path)}]

        path = get_path_to(game_map,
                            (owner.x, owner.y),
                            (point.x, point.y),
                            routing_avoid=owner.movement.routing_avoid)
        self.namespace["path"] = path

        if len(path) < 1:
            self.target_position = None
            return TreeStates.SUCCESS, []

        return TreeStates.SUCCESS, [{ResultTypes.MOVE_WITH_PATH: (owner, path)}]

class SeekTowardsLInfinityRadius(Node):
    """Seek to stay a fixed radius from a target."""
    def __init__(self, radius):
        self.radius = radius

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        if not target:
            return TreeStates.FAILURE, []

        path = move_to_radius_of_target(
            game_map,
            (owner.x, owner.y),
            (target.x, target.y),
            radius=self.radius,
            routing_avoid=owner.movement.routing_avoid)

        self.namespace["path"] = path

        if len(path) < 1:
            self.target_position = None
            return TreeStates.SUCCESS, []

        return TreeStates.SUCCESS, [{ResultTypes.MOVE_WITH_PATH: (owner, path)}]

class Skitter(Node):
    """Move the owner to a random adjacent tile."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        results = [{ResultTypes.MOVE_RANDOM_ADJACENT: owner}]
        return TreeStates.SUCCESS, results

class Swarm(Node):
    """Have an entity attempt to follow another entity of a particular species.
    The entity will try and find an entity within [radius] squares that moved in
    its last turn and move towards it.

    Parameters
    ----------
    species: etc.enum.Species
        The species of entity that the owner will follow.
    radius: int
        How far away to look for other entities of the given species.
        Default: 3
    follow_chance: int
         Likely hood that the entity will swarm.
         Default: 75

    Attributes
    ----------
    species: etc.enum.Species
        The species of entity that the owner will follow.
    radius: int
        How far away to look for other entities of the given species.
        Default: 3
    follow_chance: int
         Likely hood that the entity will swarm.
         Default: 75

    """
    def __init__(self, species, radius = 3, follow_chance = 75):
        self.species = species
        self.radius = radius
        self.chance = follow_chance

    def tick(self, owner, game_map):
        super().tick(owner, game_map)

        if randint(1,100) < self.chance:
            npcs = game_map.current_level.entities.find_all_closest(owner.point, self.species, radius=self.radius)
            moved = []
            for npc in npcs:
                if npc.movement and npc.movement.has_moved:
                    moved.append(npc)

            if len(moved) > 0:
                follow_npc = choice(moved)

                path = get_path_to(game_map,
                                    (owner.x, owner.y),
                                    (follow_npc.x, follow_npc.y),
                                    routing_avoid=owner.movement.routing_avoid)

                if len(path) > 0:
                    return TreeStates.SUCCESS, [{ResultTypes.MOVE_WITH_PATH: (owner, path)}]

        return TreeStates.FAILURE, []

class SpawnEntity(Node):
    """Spawn an entity beside the current enity.

    Parameters
    ----------
    maker: method
        The method to generate the spawn entity.
    hatch: bool
        Set to true if the new entity should replace the current entity.
        Default: False
    min_time: int
         Mininum number of turns before attempting to spawn.
         Default: 5
    max_time: int
        Maximium number of turns before spawning.
        Default: 10

    Attributes
    ----------
    maker: method
        The method to generate the spawn entity.
    current_time: int
        Number of turns since last spawn.
    hatch: bool
        If the new entity should replace the current entity.
    min_time: int
         Mininum number of turns before attempting to spawn.
    max_time: int
        Maximium number of turns before spawning.

    """
    def __init__(self, maker, hatch = False, min_time = 5, max_time = 10):
        self.current_time = 0
        self.hatch = hatch
        self.maker = maker
        self.min_time = min_time
        self.max_time = max_time

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        self.current_time += 1
        if self.current_time < self.min_time:
            return TreeStates.FAILURE, []

        if owner.children and not owner.children.can_have_children:
                return TreeStates.FAILURE, []

        if self.current_time > self.max_time or (uniform(0, 1) , (self.current_time/self.max_time)):
            x, y = random_adjacent((owner.x, owner.y))

            if (game_map.current_level.walkable[x, y]
                and not game_map.current_level.blocked[x, y]):
                entity = self.maker(Point(x, y))
                target = self.namespace.get("target")
                if target:
                    entity.ai.set_target(target)

                results = [{ResultTypes.ADD_ENTITY: entity}]
                if self.hatch:
                    results.append({ResultTypes.REMOVE_ENTITY: owner})

                if owner.children:
                    owner.children.addChild(entity)

                self.current_time = 0
                return TreeStates.SUCCESS, results
            else:
                logging.info(f"{owner} can't spawn {self.maker} as no room.")
        return TreeStates.FAILURE, []

class TravelToRandomPosition(Node):
    """Pick a random position on the map and walk towards it until getting
    there. Once there, a new target is picked.

    Attributes:
        target_position: the target point
    """
    def __init__(self):
        self.target_position = None

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        if not self.target_position or (self.target_position == owner.point):
            self.target_position = random_walkable_position(game_map, owner)

        path = self.namespace.get("path")

        blocking_entity = None
        if path and len(path) > 1:
            if not game_map.current_level.blocked[path[1][0], path[1][1]]:
                path.pop(0)
                return TreeStates.SUCCESS, [{ResultTypes.MOVE_WITH_PATH: (owner, path)}]
            else:
                if self.target_position == Point(path[1][0], path[1][1]):
                    self.target_position = None
                    return TreeStates.SUCCESS, []
                else:
                    blocking_entity = (path[1][0], path[1][1])

        path = get_path_to(game_map,
                            (owner.x, owner.y),
                            (self.target_position.x, self.target_position.y),
                            routing_avoid=owner.movement.routing_avoid,
                            blocking_entity = blocking_entity)

        self.namespace["path"] = path

        if len(path) < 1:
            self.target_position = None
            return TreeStates.SUCCESS, []

        return TreeStates.SUCCESS, [{ResultTypes.MOVE_WITH_PATH: (owner, path)}]

class PointToTarget(Node):
    def __init__(self, target_point, target_point_name):
        self.target_point = target_point
        self.target_point_name = target_point_name

    """The owner attackes the target."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        self.namespace[self.target_point_name] = self.target_point

        return TreeStates.SUCCESS, []

class PickUp(Node):
    def tick(self, owner, game_map):
        super().tick(owner, game_map)

        item = self.namespace.get("item")

        if item:
            del self.namespace["item"]

            return TreeStates.SUCCESS, [{ResultTypes.ADD_ITEM_TO_INVENTORY: item}]

        return TreeStates.FAILURE, []
