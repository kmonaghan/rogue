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
    walkable = make_walkable_array(level_map, routing_avoid=routing_avoid)
    # The cell the the source and target occupy needs to manually be set to
    # walkable, else the entity will be frozen in place.
    walkable[source[0], source[1]] = True
    walkable[target[0], target[1]] = True
    pathfinder = tcod.path.AStar(walkable.T, diagonal=1.0)
    path = pathfinder.get_path(source[0], source[1], target[0], target[1])
    return path

def make_walkable_array(level_map, routing_avoid=None):
    """Return a boolean array indicating which squares are accable to be routed
    through for some entity.

    Parameters
    ----------
    level_map: GameMap object

    routing_avoid: List of RoutingOptions
      A list containing square types which need to be avoided during routing.

    Returns
    -------
    valid_to_route: np.array or bool
      A boolean array indicating which squares are valid to route through.
    """
    if not routing_avoid:
        routing_avoid = []
    walkable = level_map.walkable.copy()
    if RoutingOptions.AVOID_DOORS in routing_avoid:
        walkable = walkable * (1 - level_map.door)
    if RoutingOptions.AVOID_MONSTERS in routing_avoid:
        walkable = walkable * (1 - level_map.blocked)
    if RoutingOptions.AVOID_WATER in routing_avoid:
        walkable = walkable * (1 - level_map.water)
    if RoutingOptions.AVOID_FIRE in routing_avoid:
        walkable = walkable * (1 - level_map.fire)
    if RoutingOptions.AVOID_STEAM in routing_avoid:
        walkable = walkable * (1 - level_map.steam)
    if RoutingOptions.AVOID_STAIRS in routing_avoid:
        if level_map.upward_stairs_position:
            walkable[level_map.upward_stairs_position] = False
        if level_map.downward_stairs_position:
            walkable[level_map.downward_stairs_position] = False
    return walkable
