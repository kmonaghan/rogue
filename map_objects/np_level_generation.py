import tcod
import numpy as np
from random import randint

from etc.enum import Tiles

from map_objects.np_dungeonGeneration import dungeonGenerator
from map_objects.np_level_map import LevelMap
from map_objects.np_prefab import Prefab
from map_objects.prefab import boss_room

from utils.utils import matprint

def levelOneGenerator(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    addCaves(dm)

    number_of_water_areas = randint(0,3)
    for i in range(number_of_water_areas):
        dm.waterFeature()

    x1, y1 = placeStairAlongEdge(dm)

    stairs = np.where(dm.grid == Tiles.STAIRSFLOOR)
    cavern = np.where(dm.grid == Tiles.CAVERN_FLOOR)

    weights = [(Tiles.CORRIDOR_FLOOR, 1),
                (Tiles.ROOM_WALL, 8),
                (Tiles.EMPTY, 9),
                (Tiles.CAVERN_FLOOR, 1),
                (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1)]

    #print(f"Route from {stairs[0][0]},{stairs[1][0]} to {cavern[0][0]},{cavern[1][0]}")
    dm.route_between(stairs[0][0], stairs[1][0], cavern[0][0], cavern[1][0], avoid=[], weights = weights, overwrite = True, tile=Tiles.CAVERN_FLOOR)

    x2, y2 = placeExitRoom(dm, x1, y1)

    if not x2:
        print("No exit, just start again")
        return levelOneGenerator(map_width, map_height)

    #print(f"Route from {x2},{y2} to {cavern[0][0]},{cavern[1][0]}")
    dm.route_between(x2, y2, cavern[0][0], cavern[1][0], avoid=[], weights = weights, overwrite = True, tile=Tiles.CAVERN_FLOOR)

    dm.cleanUpMap()

    dm.grid[0] = Tiles.CAVERN_WALL
    dm.grid[-1] = Tiles.CAVERN_WALL
    dm.grid[:, 0] = Tiles.CAVERN_WALL
    dm.grid[:, -1] = Tiles.CAVERN_WALL

    if not dm.validateMap():
        print("Bad map===========D")
        return levelOneGenerator(map_width, map_height)

    return dm

def addCaves(dm):
    dm.generateCaves(46, 3)

    dm.removeAreasSmallerThan(35)

    unconnected = dm.findUnconnectedAreas()

    dm.joinUnconnectedAreas(unconnected, connecting_tile = Tiles.CAVERN_FLOOR)

def cavernLevel(dm, x, y):
    addCaves(dm)

    number_of_water_areas = randint(0,3)
    for i in range(number_of_water_areas):
        dm.waterFeature()

    x1, y1 = placeStairRoom(dm, x, y)

    stairs = np.where(dm.grid == Tiles.STAIRSFLOOR)
    cavern = np.where(dm.grid == Tiles.CAVERN_FLOOR)

    weights = [(Tiles.CORRIDOR_FLOOR, 1),
                (Tiles.ROOM_WALL, 8),
                (Tiles.EMPTY, 9),
                (Tiles.CAVERN_FLOOR, 1),
                (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1)]

    #print(f"Route from {stairs[0][0]},{stairs[1][0]} to {cavern[0][0]},{cavern[1][0]}")
    dm.route_between(stairs[0][0], stairs[1][0], cavern[0][0], cavern[1][0], avoid=[], weights = weights, overwrite = True, tile=Tiles.CAVERN_FLOOR)

    x2, y2 = placeExitRoom(dm, x1, y1)

    if not x2:
        print("No exit, just start again")
        return levelOneGenerator(map_width, map_height)

    #print(f"Route from {x2},{y2} to {cavern[0][0]},{cavern[1][0]}")
    dm.route_between(x2, y2, cavern[0][0], cavern[1][0], avoid=[], weights = weights, overwrite = True, tile=Tiles.CAVERN_FLOOR)

    dm.cleanUpMap()

    return dm

def level_cavern_rooms(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    return dm

def roomsLevel(dm, x, y):
    pass

def levelGenerator(map_width, map_height, x, y):
    dm = dungeonGenerator(width=map_width, height=map_height)

    if randint(0,1) == 0:
        cavernLevel(dm, x, y)
    else:
        roomsLevel(dm, x, y)

    if not dm.validateMap():
        print("Bad map===========D")
        return levelGenerator(map_width, map_height, x, y)

    dm.grid[0] = Tiles.CAVERN_WALL
    dm.grid[-1] = Tiles.CAVERN_WALL
    dm.grid[:, 0] = Tiles.CAVERN_WALL
    dm.grid[:, -1] = Tiles.CAVERN_WALL

    return dm

def bossLevelGenerator(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    prefab = Prefab(boss_room())

    dm.placeRoomRandomly(prefab)

    dm.placeRandomRooms(3, 15, 2, 2, 500)

    dm.generateCorridors()

    dm.connectDoors()

    stair = np.where(dm.grid == Tiles.STAIRSFLOOR)

    placeExitRoom(dm, stair[0][0], stair[1][0])

    dm.placeWalls()

    return dm

def arena(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    dm.addRoom(2, 2, 10, 10)

    dm.grid[5,5] = Tiles.STAIRSFLOOR

    dm.addRoom(25, 15, 3, 3)

    dm.grid[28,20] = Tiles.STAIRSFLOOR

    weights = [(Tiles.CORRIDOR_FLOOR, 1),
                (Tiles.ROOM_WALL, 8),
                (Tiles.EMPTY, 9),
                (Tiles.ROOM_FLOOR, 1),
                (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1)]

    #print(f"Route from {stairs[0][0]},{stairs[1][0]} to {cavern[0][0]},{cavern[1][0]}")
    dm.route_between(5, 5, 28, 20, avoid=[], weights = weights, overwrite = True, tile=Tiles.ROOM_FLOOR)

    dm.placeWalls()

    return dm

def placeStairAlongEdge(dm):
    '''
    0 = top
    1 = right side
    2 = bottom
    3 = left side
    '''
    side = randint(0, 3)

    if side == 0:
        x = randint(1, dm.width - 4)
        y = 1
    elif side == 1:
        x = dm.width - 4
        y = randint(0, dm.height - 4)
    elif side == 2:
        x = randint(1, dm.width - 4)
        y = dm.height - 4
    elif side == 3:
        x = 1
        y = randint(1, dm.height - 4)

    print(f"{dm.width},{dm.height} placing on side: {side} at {x},{y}")

    return placeStairRoom(dm, x, y)

def placeExitRoom(dm, x, y):
    _, dijkstra = dm.create_dijkstra_map(x+1,y+1, avoid = [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL, Tiles.DEEPWATER])

    max = np.amax(dijkstra)

    min = (max // 3) * 2

    min_distance = randint(min, max)

    possible_positions = np.where(dijkstra[1:dm.width - 5,1:dm.height - 5] >= min_distance)

    if (len(possible_positions) < 1):
        print('Nowhere to place exit')
        return False

    attempts = 0

    possible_tuples = list(zip(possible_positions[0],possible_positions[1]))

    placed = False

    while len(possible_tuples) > 1:
        idx = randint(0, len(possible_tuples)-1)

        x, y = possible_tuples[idx]

        print(f"Attempting to place at: {x},{y}")
        placed = placeStairRoom(dm, x, y)

        if placed:
            possible_tuples = []
        else:
            attempts += 1
            print(f"Room place attempt: {attempts}")
            del possible_tuples[idx]

    if not placed:
        print('Failed to place exit')
        return False, False

    return x, y

def placeStairRoom(dm, x, y, overlap = True):
    placed = dm.addRoom(x,y,3,3, overlap = overlap, add_walls = True)

    if not placed:
        return False, False

    dm.grid[x+1,y+1] = Tiles.STAIRSFLOOR

    return x, y
