import tcod

from etc.enum import RoutingOptions

def get_shortest_path(level_map, source, target, routing_avoid=None):
    """Get the shortest path through the game map from a source to a target
    point, while avoiding certain dungeon features.

    Parameters
    ----------
    level_map: LevelMap object

    source: (int, int)
      The source position.

    target: (int, int)
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
    walkable[source[0], source[1]] = True
    walkable[target[0], target[1]] = True
    pathfinder = tcod.path.AStar(walkable.T, diagonal=1.0)
    path = pathfinder.get_path(source[0], source[1], target[0], target[1])
    return path
