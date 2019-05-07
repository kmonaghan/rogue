import tcod
import numpy as np
from random import randint

from etc.enum import RoutingOptions
from map_objects.point import Point
from utils.utils import matprint

def get_shortest_path(level_map, source, target, routing_avoid=None):
    """Get the shortest path through the game map from a source to a target
    point, while avoiding certain dungeon features.

    Parameters
    ----------
    level_map: LevelMap object

    source: Point
      The source position.

    target: Point
      The target position.

    routing_avoid: List[RoutingOptions]
      Dungeon features to avoid in the path.

    Returns
    -------
    path: List[(int, int)]
      The path shortest path through the game map from source to target while
      avoiding the dungeon features in routing_avoid.
    """
    walkable = level_map.current_level.make_walkable_array(routing_avoid=routing_avoid)
    # The cell the the source and target occupy needs to manually be set to
    # walkable, else the entity will be frozen in place.
    walkable[source.x, source.y] = True
    walkable[target.x, target.y] = True
    pathfinder = tcod.path.AStar(walkable, diagonal=1.0)
    path = pathfinder.get_path(source.x, source.y, target.x, target.y)
    return path

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
