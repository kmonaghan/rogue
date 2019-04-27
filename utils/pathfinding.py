import tcod

from etc.enum import RoutingOptions

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
