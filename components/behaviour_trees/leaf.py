'''via https://github.com/madrury/roguelike
'''
from utils.pathfinding import get_shortest_path

from etc.enum import TreeStates
from etc.enum import ResultTypes
from utils.utils import random_walkable_position, random_adjacent
from components.behaviour_trees.root import Node

from map_objects.point import Point


class MoveTowardsTargetEntity(Node):
    """Move the owner towards a target and remember the target's point."""
    def __init__(self, target_point_name):
        self.name = target_point_name

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        if not target:
            print("No target set")
            return TreeStates.FAILURE, []

        print("MoveTowardsTargetEntity Setting to point:" + self.name)
        print(str(target))
        self.namespace[self.name] = target.point
        results = [{ResultTypes.MOVE_TOWARDS: (owner, target.x, target.y)}]
        return TreeStates.SUCCESS, results


class MoveTowardsPointInNamespace(Node):

    def __init__(self, name):
        self.name = name

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        if not self.namespace.get(self.name):
            raise ValueError(f"{self.name} is not in tree namespace!")
        point = self.namespace.get(self.name)
        if ((owner.x, owner.y) == self.namespace.get(self.name + '_previous')
            or (owner.x, owner.y) == point):
            self.namespace[self.name + '_previous'] = None
            print("MoveTowardsPointInNamespace Setting none to point:" + self.name)
            self.namespace[self.name] = None
            return TreeStates.SUCCESS, []
        results = [{ResultTypes.MOVE_TOWARDS: (owner, point.x, point.y)}]
        self.namespace[self.name + '_previous'] = (owner.x, owner.y)
        print("MoveTowardsPointInNamespace Move towards:" + str(point))
        return TreeStates.SUCCESS, results


class SeekTowardsLInfinityRadius(Node):
    """Seek to stay a fixed radius from a target."""
    def __init__(self, radius):
        self.radius = radius

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        path = get_path_to_radius_of_target(
            game_map,
            owner.point,
            target.point,
            radius=self.radius,
            routing_avoid=owner.routing_avoid)
        if len(path) <= 1:
            return TreeStates.SUCCESS, []
        results = [{
            ResultTypes.SET_POSITION: (owner, path[0][0], path[0][1])}]
        return TreeStates.SUCCESS, results

class TravelToRandomPosition(Node):
    """Pick a random position on the map and walk towards it until getting
    there.
    """
    def __init__(self):
        self.target_position = None
        self.target_path = None

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        if not self.target_position:
            self.target_position = random_walkable_position(game_map, owner)
        print("TravelToRandomPosition travelling to: " + str(self.target_position))
        self.path = get_shortest_path(
            game_map,
            owner.point,
            self.target_position,
            routing_avoid=owner.movement.routing_avoid)
        if len(self.path) < 1:
            self.target_position = None
            return TreeStates.SUCCESS, []
        results = [{
            ResultTypes.MOVE_WITH_PATH: (owner, self.path)}]
        return TreeStates.SUCCESS, results

class Skitter(Node):
    """Move the owner to a random adjacent tile."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        results = [{ResultTypes.MOVE_RANDOM_ADJACENT: owner}]
        return TreeStates.SUCCESS, results

class DoNothing(Node):
    """Take no action and pass the turn."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        return TreeStates.SUCCESS, []


class Attack(Node):
    """The owner attackes the target."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        target = self.namespace.get("target")
        if owner.offence and target.defence:
            print("Attack: SUCCESS")
            return (TreeStates.SUCCESS,
                    owner.offence.attack(target))
        else:
            print("Attack: FAILURE")
            return TreeStates.FAILURE, []

class PointToTarget(Node):
    def __init__(self, target_point, target_point_name):
        self.target_point = target_point
        self.target_point_name = target_point_name

    """The owner attackes the target."""
    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        print("Setting namespace for " + self.target_point_name)
        self.namespace[self.target_point_name] = self.target_point

        return TreeStates.SUCCESS, []

class SpawnEntity(Node):

    def __init__(self, maker):
        self.maker = maker

    def tick(self, owner, game_map):
        super().tick(owner, game_map)
        x, y = random_adjacent((owner.x, owner.y))
        if (game_map.current_level.walkable[x, y]
            and not game_map.current_level.blocked[x, y]):
            #and not game_map.current_level.water[x, y]):
            entity = self.maker(Point(x, y))
            if entity:
                #print("Will spawn " + str(entity))
                return TreeStates.SUCCESS, [{ResultTypes.ADD_ENTITY: entity}]
        return TreeStates.FAILURE, []
