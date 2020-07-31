from random import randint
from typing import List, Tuple

import numpy as np
import tcod

from etc.configuration import CONFIG
from etc.enum import RoutingOptions
from map_objects.point import Point
from utils.utils import matprint

def create_walkable_cost(game_map, routing_avoid=None, blocking_entity_cost = 10, avoid_entity = None):
    """Calculate the cost of moving into a node.
    The base cost of a walkable node is 1. If there is a blocking entity, this
    is increased by blocking_entity_cost. If avoid_entity is passed through, the
    nodes within a radius of 2 have their cost increased by a factor of five and
    nodes within a radius of 1 are increased by a factor of 10.

    Parameters
    ----------
    game_map: GameMap

    routing_avoid: List[RoutingOptions]
      Dungeon features to avoid in the path.

    blocking_entity_cost: int
      The cost to try and move through a node with a blocking entity.

    avoid_entity: Entity
      An entity than imposes a repelling effect and increases the cost of
      passing near it.

    Returns
    -------
    cost: ndarray
      The final calculated cost to move to a node.
    """
    cost = game_map.current_level.make_walkable_array(routing_avoid=routing_avoid).astype(np.int)

    if avoid_entity:
        cost[avoid_entity.x-2:avoid_entity.x+3, avoid_entity.y-2:avoid_entity.y+3] = np.multiply(cost[avoid_entity.x-2:avoid_entity.x+3, avoid_entity.y-2:avoid_entity.y+3], 5)
        cost[avoid_entity.x-1:avoid_entity.x+2, avoid_entity.y-1:avoid_entity.y+2] = np.multiply(cost[avoid_entity.x-1:avoid_entity.x+2, avoid_entity.y-1:avoid_entity.y+2], 2)
        cost[avoid_entity.x,avoid_entity.y] = cost[avoid_entity.x,avoid_entity.y] * 3

    for entity in game_map.current_level.entities:
        # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
        if entity.blocks and cost[entity.x, entity.y]:
            # Add to the cost of a blocked position.
            # A lower number means more enemies will crowd behind each other in
            # hallways.  A higher number means enemies will take longer paths in
            # order to surround the player.
            cost[entity.x, entity.y] += blocking_entity_cost

    return cost

def calculate_dijkstra(game_map, target_points = None, routing_avoid=None, blocking_entity_cost = 10, avoid_entity = None):
    """Calculate the cost of moving into a node.
    The base cost of a walkable node is 1. If there is a blocking entity, this
    is increased by blocking_entity_cost. If avoid_entity is passed through, the
    nodes within a radius of 2 have their cost increased by a factor of five and
    nodes within a radius of 1 are increased by a factor of 10.

    Parameters
    ----------
    game_map: GameMap object

    target_points: List[(int, int)]

    routing_avoid: List[RoutingOptions]
      Dungeon features to avoid in the path.

    blocking_entity_cost: int
      The cost to try and move through a node with a blocking entity.

    avoid_entity: Entity
      An entity than imposes a repelling effect and increases the cost of
      passing near it.

    Returns
    -------
    dist: ndarray
      Return the computed distance of all nodes on a 2D Dijkstra grid.
    """
    cost = create_walkable_cost(game_map, routing_avoid, blocking_entity_cost, avoid_entity)
    dist = tcod.path.maxarray(game_map.current_level.walkable.shape, dtype=np.int32)

    for x, y in target_points:
        dist[x, y] = 0

    tcod.path.dijkstra2d(dist, cost, CONFIG.get('cardinal_cost'), CONFIG.get('diagonal_cost'))

    return dist

def get_path_to(start: Tuple[int, int], destination: Tuple[int, int], game_map, routing_avoid=None) -> List[Tuple[int, int]]:
    """Calculate the cost of moving into a node.
    The base cost of a walkable node is 1. If there is a blocking entity, this
    is increased by blocking_entity_cost. If avoid_entity is passed through, the
    nodes within a radius of 2 have their cost increased by a factor of five and
    nodes within a radius of 1 are increased by a factor of 10.

    Parameters
    ----------
    start: Tuple(int, int)
        Where the path will start.

    destination: Tuple(int, int)
        Where the path should end.

    game_map: GameMap

    target_points: List[(int, int)]

    routing_avoid: List[RoutingOptions]
      Dungeon features to avoid in the path.

    Returns
    -------
    path: List[Tuple[int, int]]
      Return a list of all the nodes between the start node and destination node.
    """
    cost = create_walkable_cost(game_map, routing_avoid=routing_avoid)
    #start point needs to be passable.
    cost[start[0], start[1]] = 1

    graph = tcod.path.SimpleGraph(cost=cost,
                                    cardinal=CONFIG.get('cardinal_cost'),
                                    diagonal=CONFIG.get('diagonal_cost'))

    pathfinder = tcod.path.Pathfinder(graph)

    pathfinder.add_root(start)  # Start position.

    # Compute the path to the destination and remove the starting point.
    path: List[List[int]] = pathfinder.path_to(destination)[1:].tolist()
    # Convert from List[List[int]] to List[Tuple[int, int]].
    return [(index[0], index[1]) for index in path]

def move_to_radius_of_target(game_map, source, target, radius,
                                 routing_avoid=None):
    aslice = game_map.current_level.dijkstra_player[source.x-1:source.x+2, source.y-1:source.y+2].copy()
    if aslice[1,1] == radius:
        return source

    if aslice[1,1] > radius:
        #We want to roll down the hill
        aslice[aslice == 0] = 99
        target_value = np.amin(aslice)

    else:
        #Back up the hill
        target_value = np.amax(aslice)

    if aslice[1,1] == target_value:
        return source

    itemindex = np.where(aslice==target_value)

    idx = randint(0, len(itemindex[0]) - 1)

    return translate_point(source, itemindex[0][idx], itemindex[1][idx])

def translate_point(point, x, y):

    offsets = [[(-1, -1), (0, -1), (-1, 1)],
                [(1, 0), (0, 0), (-1, 0)],
                [(1, -1), (0, 1), (1, 1)]]

    (a, b) = offsets[x][y]

    change = Point(point.x + a, point.y + b)

    return change
