'''via https://github.com/madrury/roguelike
'''

import random

from etc.enum import TreeStates
from components.behaviour_trees.root import Node
from map_objects.point import Point

class InNamespace(Node):
    """Check if a variable is set within the tree's namespace.

    Attributes
    ----------
    name: str
      The name of the variable in the tree's namespace.
    """
    def __init__(self, name):
        self.name = name

    def tick(self, owner, game_map):
        if self.namespace.get(self.name):
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class IsAdjacent(Node):
    """Return sucess is owner is adjacent to target."""
    def tick(self, owner, game_map):
        target = self.namespace.get("target")
        if not target:
            return TreeStates.FAILURE, []

        distance = owner.point.distance_to(target.point)
        if distance < 2:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class WithinPlayerFov(Node):
    """Return success if owner is in the player's fov."""
    def tick(self, owner, game_map):
        if game_map.current_level.fov[owner.x, owner.y]:
            return TreeStates.SUCCESS, []
        return TreeStates.FAILURE, []


class WithinL2Radius(Node):
    """Return success if the distance between owner and target is less than or
    equal to some radius.
    """
    def __init__(self, radius):
        self.radius = radius

    def tick(self, owner, game_map):
        target = self.namespace.get("target")
        distance = owner.point.distance_to(target.point)
        if distance <= self.radius:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class AtLInfinityRadius(Node):
    """Return success if the owner is at exactly a given Linfinity norm
    radius.
    """
    def __init__(self, radius):
        self.radius = radius

    def tick(self, owner, game_map):
        target = self.namespace.get("target")
        l_inf_distance = max(abs(owner.x - target.x), abs(owner.y - target.y))
        if l_inf_distance == self.radius:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class CoinFlip(Node):

    def __init__(self, p=0.5):
        self.p = p

    def tick(self, owner, game_map):
        if random.uniform(0, 1) < self.p:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class OutsideL2Radius(Node):
    """Return success if the distance between owner and target is less than or
    equal to some radius.
    """
    def __init__(self, radius):
        self.radius = radius

    def tick(self, owner, game_map):
        radius_point = self.namespace.get("radius_point")

        if not radius_point:
            print("Nothing to check for outside of radius.")
            return

        distance = owner.point.distance_to(radius_point)
        if distance > self.radius:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []

class IsFinished(Node):

    def __init__(self, number_of_turns=10):
        self.number_of_turns = number_of_turns

    def tick(self, owner, game_map):
        if self.number_of_turns <= 0:
            return TreeStates.SUCCESS, []
        else:
            owner.ai.number_of_turns -= 1
            return TreeStates.FAILURE, []

class ChangeAI(Node):

    def __init__(self, ai):
        self.ai = ai

    def tick(self, owner, game_map):
        owner.del_component('ai')
        owner.add_component(ai, 'ai')
        return TreeStates.SUCCESS, []

class FindNearestTargetEntity(Node):

        def __init__(self, range = 2, species_type = None):
            self.range = range
            self.species = species_type

        def tick(self, owner, game_map):
            target = game_map.current_level.find_closest_entity(owner, self.range, self.species)

            if target:
                print("FindNearestTargetEntity: " + str(target))
                self.namespace["target"] = target

                return TreeStates.SUCCESS, []
            else:
                return TreeStates.FAILURE, []
