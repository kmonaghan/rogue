import os.path
import numpy as np
import math
import sys
import random

from map_objects.point import Point

def flatten_list_of_dictionaries(list_of_dictionaries):
    ret = []
    for d in list_of_dictionaries:
        for k, v in d.items():
            ret.append({k: v})
    return ret

def get_key_from_single_key_dict(d):
    return list(d)[0]

def unpack_single_key_dict(d):
    k = list(d)[0]
    return k, d[k]

def choose_from_list_of_tuples(list_of_tuples):
    """Randomly sample from a catagorical distribution defined by a list
    of (probability, catagory) tuples.
    """
    probs, choices = zip(*list_of_tuples)
    return np.random.choice(choices, size=1, p=probs)[0]

#-----------------------------------------------------------------------------
# Geometric operations.
#-----------------------------------------------------------------------------
def l2_distance(source, target):
    dx = target[0] - source[0]
    dy = target[1] - source[1]
    return math.sqrt(dx*dx + dy*dy)

def coordinates_on_circle(center, radius):
    circle = set()
    circle.update((center[0] + radius - i, center[1] + i)
        for i in range(0, radius + 1))
    circle.update((center[0] - radius + i, center[1] - i)
        for i in range(0, radius + 1))
    circle.update((center[0] - radius + i, center[1] + i)
        for i in range(0, radius + 1))
    circle.update((center[0] + radius - i, center[1] - i)
        for i in range(0, radius + 1))
    return circle

def coordinates_within_circle(center, radius):
    circle = set()
    for r in range(0, radius + 2):
        circle.update(coordinates_on_circle(center, r))
    return circle

def adjacent_coordinates(center):
    dxdy = [(-1, 1), (0, 1), (1, 1),
            (-1, 0),         (1, 0),
            (-1, -1), (0, -1), (1, -1)]
    return [(center[0] + dx, center[1] + dy) for dx, dy in dxdy]

def _bresenham_ray(game_map, source, target):
    """Bresenham's line drawing algorithm, used to draw a ray joining two
    points.

    Modified from the example at rosettacode:

    https://rosettacode.org/wiki/Bitmap/Bresenham%27s_line_algorithm#Python

    Returns a list of tuples for the ray, and the index into the ray at which
    the target position lies.
    """
    ray = []
    (x0, y0), (x1, y1) = source, target
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    idx, target_idx = 0, 0
    if dx > dy:
        err = dx / 2.0
        while game_map.within_bounds(x, y) and game_map.walkable[x, y]:
            ray.append((x, y))
            if (x, y) == target:
                target_idx = idx
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
            idx += 1
    else:
        err = dy / 2.0
        while game_map.within_bounds(x, y) and game_map.walkable[x, y]:
            ray.append((x, y))
            if (x, y) == target:
                target_idx = idx
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
            idx += 1
    if target_idx == 0:
        target_idx = idx
    return ray, idx, target_idx

def bresenham_line(game_map, source, target):
    ray, _, target_idx = _bresenham_ray(game_map, source, target)
    return ray[:target_idx]

def bresenham_ray(game_map, source, target):
    ray, last_idx, target_idx = _bresenham_ray(game_map, source, target)
    return ray[:last_idx]

#-----------------------------------------------------------------------------
# Choosing random map positions.
#-----------------------------------------------------------------------------
def random_adjacent(center):
    x, y = center
    candidates = [
        (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
        (x - 1, y),                 (x + 1, y),
        (x - 1, y - 1), (x, y - 1), (x + 1, y + 1)]
    return random.choice(candidates)

def random_walkable_position(game_map, entity):
    walkable_array =  game_map.current_level.make_walkable_array(entity.movement.routing_avoid)
    walkable_array[entity.x, entity.y] = True
    open_tiles = np.where(walkable_array == True)
    listOfCoordinates = list(zip(open_tiles[0], open_tiles[1]))

    target = random.choice(listOfCoordinates)
    return Point(target[0], target[1])

#-----------------------------------------------------------------------------
# Numpy helper functions
#-----------------------------------------------------------------------------

def matprint(mat, fmt="g"):
    with np.printoptions(threshold=np.inf, linewidth=2000):
        print(mat)

#-----------------------------------------------------------------------------
# Helper functions.
#-----------------------------------------------------------------------------

def find(f, seq):
    """via https://tomayko.com/blog/2004/cleanest-python-find-in-list-function """
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item

    return None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
