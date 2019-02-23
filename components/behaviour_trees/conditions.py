'''via https://github.com/madrury/roguelike
'''

import random

from etc.enum import TreeStates
from components.behaviour_trees.root import Node
from map_objects.point import Point

class InNamespace(Node):

    def __init__(self, name):
        self.name = name

    def tick(self, owner, target, game_map):
        if self.namespace.get(self.name):
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []

class IsAdjacent(Node):
    """Return sucess is owner is adjacent to target."""
    def tick(self, owner, target, game_map):
        distance = owner.point.distance_to(target.point)
        if distance < 2:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class WithinFov(Node):
    """Return success if owner is in the players fov."""
    def tick(self, owner, target, game_map):
        if game_map.fov[owner.x, owner.y]:
            return TreeStates.SUCCESS, []
        return TreeStates.FAILURE, []


class WithinL2Radius(Node):
    """Return success if the distance between owner and target is less than or
    equal to some radius.
    """
    def __init__(self, radius):
        self.radius = radius

    def tick(self, owner, target, game_map):
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

    def tick(self, owner, target, game_map):
        l_inf_distance = max(abs(owner.x - target.x), abs(owner.y - target.y))
        if l_inf_distance == self.radius:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []


class CoinFlip(Node):

    def __init__(self, p=0.5):
        self.p = p

    def tick(self, owner, target, game_map):
        if random.uniform(0, 1) < self.p:
            return TreeStates.SUCCESS, []
        else:
            return TreeStates.FAILURE, []