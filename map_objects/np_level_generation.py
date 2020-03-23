import tcod
import numpy as np
from random import choice, randint

from etc.enum import Tiles
from etc.exceptions import FailedToPlaceEntranceError, FailedToPlaceExitError, BadMapError, FailedToPlaceRoomError, MapNotEnoughExitsError

from map_objects.np_dungeonGeneration import dungeonGenerator, cellular_map
from map_objects.np_level_map import LevelMap
from map_objects.np_prefab import Prefab
from map_objects.prefab import boss_room, treasure_room, barracks, stair_room, prison_block, necromancer_lair, list_of_prefabs

from utils.utils import matprint

def levelOneGenerator(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    addCaves(dm)

    number_of_water_areas = randint(0,3)
    for i in range(number_of_water_areas):
        dm.waterFeature()

    x1, y1, entrance = placeStairAlongEdge(dm)

    if not entrance:
        raise FailedToPlaceEntranceError

    entrance_doors = doors = np.where(entrance.layout == Tiles.DOOR)
    cavern = np.where(dm.grid == Tiles.CAVERN_FLOOR)

    tile_index = randint(0, len(cavern[0])-1)

    weights = [(Tiles.CORRIDOR_FLOOR, 1),
                (Tiles.CAVERN_FLOOR, 1),
                (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1),
                (Tiles.CAVERN_WALL, 3),
                (Tiles.EMPTY, 5),
                ]

    for idx, door_x in enumerate(entrance_doors[0]):
        door_y = entrance_doors[1][idx]
        door_x = door_x + entrance.x
        door_y = door_y + entrance.y
        dm.route_between(door_x, door_y, cavern[0][tile_index], cavern[1][tile_index], avoid=[Tiles.ROOM_WALL], weights = weights, tile=Tiles.CAVERN_FLOOR)

    x2, y2, exit_room = placeExitRoom(dm, x1, y1, add_door = True)

    if not exit_room:
        raise FailedToPlaceExitError

    exit_doors = doors = np.where(exit_room.layout == Tiles.DOOR)

    for idx, door_x in enumerate(exit_doors[0]):
        door_y = exit_doors[1][idx]
        door_x = door_x + exit_room.x
        door_y = door_y + exit_room.y
        dm.route_between(door_x, door_y, cavern[0][tile_index], cavern[1][tile_index], avoid=[Tiles.ROOM_WALL], weights = weights, tile=Tiles.CAVERN_FLOOR)

    prefab = Prefab(treasure_room)

    room = dm.placeRoomRandomly(prefab)

    if room:
        doors = np.where(room.layout == Tiles.DOOR)

        x3 = doors[0][0] + room.x
        y3 = doors[1][0] + room.y

        tile_index = randint(0, len(cavern[0])-1)

        dm.route_between(x3, y3, cavern[0][tile_index], cavern[1][tile_index], avoid=[Tiles.ROOM_WALL], weights = weights, tile=Tiles.CAVERN_FLOOR)

    place_foliage(dm)

    dm.cleanUpMap()

    if not dm.validateMap():
        raise BadMapError

    return dm

def addCaves(dm):
    dm.generateCaves(46, 3)

    dm.removeAreasSmallerThan(35)

    unconnected = dm.findUnconnectedAreas()

    dm.joinUnconnectedAreas(unconnected, connecting_tile = Tiles.CAVERN_FLOOR)

    place_foliage(dm)

def cavernLevel(dm, x, y):
    addCaves(dm)

    number_of_water_areas = randint(0,3)
    for i in range(number_of_water_areas):
        dm.waterFeature()

    x1, y1, room = placeStairRoom(dm, x, y, name="entrance")

    stairs = np.where(dm.grid == Tiles.STAIRS_FLOOR)
    cavern = np.where(dm.grid == Tiles.CAVERN_FLOOR)

    weights = [(Tiles.CORRIDOR_FLOOR, 1),
                (Tiles.ROOM_WALL, 8),
                (Tiles.EMPTY, 9),
                (Tiles.CAVERN_FLOOR, 1),
                (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1)]

    dm.route_between(stairs[0][0], stairs[1][0], cavern[0][0], cavern[1][0], avoid=[], weights = weights, tile=Tiles.CAVERN_FLOOR)

    x2, y2, exit_room = placeExitRoom(dm, x1, y1)

    if not x2:
        raise FailedToPlaceExitError

    dm.route_between(x2, y2, cavern[0][0], cavern[1][0], avoid=[], weights = weights, tile=Tiles.CAVERN_FLOOR)

    dm.cleanUpMap()

def level_cavern_rooms(dm, x, y):
    square_height = dm.width // 3

    overwrite = randint(0,1)

    cavern_width = randint(square_height, (dm.width * 3) // 4)
    cavern_height = randint(square_height, (dm.height * 3) // 4)

    width_offset = randint(0, dm.width - cavern_width - 1)
    height_offset = randint(0, dm.height - cavern_height - 1)

    x1, y1, room = placeStairRoom(dm, x, y, name="entrance", add_door = True)

    tempgrid = dm.grid.copy()
    tempgrid[x1-(square_height//2):x1+(square_height//2), y1-(square_height//2):y1+(square_height//2)] = Tiles.IMPENETRABLE
    tempgrid[:, -4:dm.width] = Tiles.IMPENETRABLE
    tempgrid[-4:dm.width] = Tiles.IMPENETRABLE
    empties = np.where(tempgrid == 0)

    tile_index = randint(0, len(empties[0])-1)

    placeStairRoom(dm, empties[0][tile_index], empties[1][tile_index], name="exit", add_door = True)

    if overwrite == 1:
        dm.grid[width_offset:width_offset+cavern_width, height_offset:height_offset+cavern_height] = Tiles.IMPENETRABLE

    dm.placeRandomRooms((square_height//4), square_height-2, 2, 2, add_door = True, add_walls = True, attempts=5000)

    cells = cellular_map(shape=(cavern_width,cavern_height), probability=43)

    slice = dm.grid[width_offset:width_offset+cavern_width, height_offset:height_offset+cavern_height]

    if overwrite == 1:
        slice[:] = cells[:]
        slice[np.where(cells == 1)] = Tiles.CAVERN_FLOOR
    else:
        slice[np.where((cells == 1) & (slice == Tiles.EMPTY))] = Tiles.CAVERN_FLOOR

    for i in range (5):
        x, y = dm.findEmptySpace()

        if not x and not y:
            continue
        else:
            dm.generateCorridors(x = x, y = y)

    dm.connectRooms()

    unconnected = dm.findUnconnectedAreas()

    dm.joinUnconnectedAreas(unconnected, connecting_tile = Tiles.CAVERN_FLOOR)

    place_foliage(dm)

    dm.cleanUpMap()

    return dm

def roomsLevel(dm, x, y):
    square_height = dm.width // 3

    x1, y1, room = placeStairRoom(dm, x, y, name="entrance", add_door = True)

    tempgrid = dm.grid.copy()
    tempgrid[x1-(square_height//2):x1+(square_height//2), y1-(square_height//2):y1+(square_height//2)] = Tiles.IMPENETRABLE
    tempgrid[:, -4:dm.width] = Tiles.IMPENETRABLE
    tempgrid[-4:dm.width] = Tiles.IMPENETRABLE
    empties = np.where(tempgrid == 0)

    tile_index = randint(0, len(empties[0])-1)

    placeStairRoom(dm, empties[0][tile_index], empties[1][tile_index], name="exit", add_door = True)

    placePrefabs(dm, overwrite=False)

    dm.placeRandomRooms((square_height//4), square_height-2, 2, 2, add_door = True, add_walls = True, attempts=5000)

    for i in range (5):
        x, y = dm.findEmptySpace()

        if not x and not y:
            continue
        else:
            dm.generateCorridors(x = x, y = y)

    dm.connectRooms()

    dm.cleanUpMap()

def placePrefabs(dm, overwrite=True):
    number_of_prefabs = randint(0, len(list_of_prefabs)-1)

    for x in range(number_of_prefabs):
        prefab = Prefab(choice(list_of_prefabs))

        room = dm.placeRoomRandomly(prefab, overwrite=overwrite)

    return dm

def levelGenerator(map_width, map_height, x, y):
    dm = dungeonGenerator(width=map_width, height=map_height)
    x = x - 2
    y = y - 2
    levelType = randint(0,3)
    result = False

    if levelType == 0:
        result = roomsLevel(dm, x, y)
    elif levelType == 1:
        result = cavernLevel(dm, x, y)
    elif levelType == 2:
        result = level_cavern_rooms(dm, x, y)

    if not dm.validateMap():
        raise BadMapError

    return dm

def bossLevelGenerator(map_width, map_height, x, y):
    dm = dungeonGenerator(width=map_width, height=map_height)

    x1, y1, room = placeStairRoom(dm, x, y, name="entrance")

    addCaves(dm)

    prefab = Prefab(boss_room)

    room = dm.placeRoomRandomly(prefab)

    door = np.where(room.layout == Tiles.DOOR)

    x2 = room.x + door[0][0]
    y2 = room.y + door[1][0]

    cavern = np.where(dm.grid == Tiles.CAVERN_FLOOR)

    weights = [(Tiles.CORRIDOR_FLOOR, 1),
                (Tiles.ROOM_WALL, 8),
                (Tiles.EMPTY, 9),
                (Tiles.CAVERN_FLOOR, 1),
                (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1)]

    dm.route_between(x, y, cavern[0][0], cavern[1][0], avoid=[], weights = weights, tile=Tiles.CAVERN_FLOOR)

    dm.route_between(x2, y2, cavern[0][0], cavern[1][0], avoid=[Tiles.ROOM_WALL, Tiles.ROOM_FLOOR], weights = weights, tile=Tiles.CAVERN_FLOOR)

    dm.cleanUpMap()

    return dm

def arena(map_width, map_height, x = 5, y = 5):
    dm = dungeonGenerator(width=map_width, height=map_height)

    room = dm.addRoom(10, 10, 10, 10, add_walls=True, add_door=True, max_doors = 1)

    #room = dm.addCircleShapedRoom(10, 10, 5, add_walls=True, add_door=True, max_doors = 1)

    cave = dm.addRoom(14, 24, 4, 4, add_door=False, add_walls = True, tile = Tiles.CAVERN_FLOOR, max_doors = 1)

    room2 = dm.addRoom(25, 25, 3, 3, add_walls=True, add_door=True, max_doors = 1)

    '''
    prefab = Prefab(barracks)

    room = dm.placeRoomRandomly(prefab)
    x1,y1 = room.exits[0]
    x1 = x1 + room.x
    y1 = y1 + room.y

    weights = [(Tiles.EMPTY, 1)]

    dm.route_between(18, 29, x1, y1, avoid = [], weights = weights, avoid_rooms=True)
    '''
    dm.cleanUpMap()

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
        x = randint(0, dm.width - 5)
        y = 0
    elif side == 1:
        x = dm.width - 5
        y = randint(0, dm.height - 5)
    elif side == 2:
        x = randint(0, dm.width - 5)
        y = dm.height - 5
    elif side == 3:
        x = 0
        y = randint(0, dm.height - 5)

    return placeStairRoom(dm, x, y, name="entrance")

def placeExitRoom(dm, x, y, add_door = False):
    _, dijkstra = dm.create_dijkstra_map(x+1,y+1, avoid = [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL, Tiles.DEEP_WATER], avoid_rooms=True)

    max = np.amax(dijkstra)

    min = (max // 3) * 2

    min_distance = randint(min, max)

    possible_positions = np.where(dijkstra[1:dm.width - 5,1:dm.height - 5] >= min_distance)

    if (len(possible_positions) < 1):
        raise FailedToPlaceExitError

    attempts = 0

    possible_tuples = list(zip(possible_positions[0],possible_positions[1]))

    placed = False

    while len(possible_tuples) > 1:
        idx = randint(0, len(possible_tuples)-1)

        x, y = possible_tuples[idx]

        x1, y1, placed = placeStairRoom(dm, x, y, name="exit", add_door=add_door)

        if placed:
            possible_tuples = []
        else:
            attempts += 1
            del possible_tuples[idx]

    if not placed:
        raise FailedToPlaceExitError

    return x, y, placed

def placeStairRoom(dm, x, y, overlap = True, name="", add_door = False):
    placed = dm.addRoom(x,y,3,3, overlap = overlap, add_walls = True, add_door = True, name = name, max_doors=1)

    x1, y1 = placed.center
    dm.grid[x1,y1] = Tiles.STAIRS_FLOOR

    return x, y, placed

def squares(dm, x, y):
    square_height = dm.width // 3

    #dm.grid[square_height] = Tiles.IMPENETRABLE
    #dm.grid[square_height*2] = Tiles.IMPENETRABLE
    #dm.grid[:, square_height] = Tiles.IMPENETRABLE
    #dm.grid[:, square_height*2] = Tiles.IMPENETRABLE

    x1, y1, room = placeStairRoom(dm, x, y, name="entrance", add_door = True)

    tempgrid = dm.grid.copy()
    tempgrid[x1-(square_height//2):x1+(square_height//2), y1-(square_height//2):y1+(square_height//2)] = Tiles.IMPENETRABLE
    tempgrid[:, -4:dm.width] = Tiles.IMPENETRABLE
    tempgrid[-4:dm.width] = Tiles.IMPENETRABLE
    empties = np.where(tempgrid == 0)

    tile_index = randint(0, len(empties[0])-1)

    placeStairRoom(dm, empties[0][tile_index], empties[1][tile_index], name="exit", add_door = True)

    placePrefabs(dm, overwrite=False)

    dm.placeRandomRooms((square_height//4), square_height-2, 2, 2, add_door = True, add_walls = True, attempts=5000)

    for i in range (5):
        x, y = dm.findEmptySpace()

        if not x and not y:
            continue
        else:
            dm.generateCorridors(x = x, y = y)

    dm.connectRooms()

    dm.cleanUpMap()

    return dm

def place_foliage(dm):
    cells = cellular_map(shape=dm.grid.shape, probability=60)

    dm.grid[np.where((dm.grid == Tiles.CAVERN_FLOOR) & (cells == 1))] = Tiles.FUNGAL_CAVERN_FLOOR
