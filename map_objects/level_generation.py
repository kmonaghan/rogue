import tcod

from map_objects.dungeonGenerator import *
from map_objects.level_map import LevelMap
from map_objects.prefab import *

def level_one_generator(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    cave_width = int((map_width * 2)/ 3)
    caves = dungeonGenerator(width=cave_width, height=map_height - 2)

    caves.generateCaves(44, 3)
    # clear away small islands
    unconnected = caves.findUnconnectedAreas()
    for area in unconnected:
        if len(area) < 35:
            for x, y in area:
                caves.dungeon.grid[x][y] = Tiles.EMPTY

    for x, y, tile in caves:
        dm.dungeon.grid[x][y + 1] = caves.dungeon.grid[x][y]

    dm.findCaves()
    #dm.findAlcoves()

    startY = randint(1, dm.dungeon.height - 6)
    dm.placeRoom(1, startY, 5, 5, ignoreOverlap = True)

    dm.placeRandomRooms(5, 9, 2, 2, 500)
    x, y = dm.findEmptySpace(3)
    while x:
        dm.generateCorridors('f', x, y)
        x, y = dm.findEmptySpace(3)
    # join it all together
    dm.connectAllRooms(0)

    unconnected = dm.findUnconnectedAreas()
    dm.joinUnconnectedAreas(unconnected)

    dm.findDeadends()
    while len(dm.dungeon.deadends):
        dm.pruneDeadends(1)

    dm.placeWalls()
    dm.closeDeadDoors()

    return LevelMap(dm.dungeon)

def level_caverns(dm):
    dm.generateCaves(45, 4)
    # clear away small islands
    unconnected = dm.findUnconnectedAreas()
    for area in unconnected:
        if len(area) < 10:
            for x, y in area:
                dm.dungeon.grid[x][y] = Tiles.EMPTY

    unconnected = dm.findUnconnectedAreas()
    dm.joinUnconnectedAreas(unconnected, Tiles.CAVERN_FLOOR)

    dm.findCaves()
    dm.placeWalls()

    return dm

def level_cavern_rooms(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    dm.generateCaves(37, 4)
    # clear away small islands
    unconnected = dm.findUnconnectedAreas()
    for area in unconnected:
        if len(area) < 35:
            for x, y in area:
                dm.dungeon.grid[x][y] = Tiles.EMPTY

    dm.findCaves()

    # generate rooms and corridors
    dm.placeRandomRooms(5, 10, 1, 1, 1000)
    x, y = dm.findEmptySpace(3)
    while x:
        dm.generateCorridors('f', x, y)
        x, y = dm.findEmptySpace(3)

    # join it all together
    dm.connectAllRooms(0)

    unconnected = dm.findUnconnectedAreas()
    dm.joinUnconnectedAreas(unconnected)

    #clear all dead ends
    dm.findDeadends()
    while dm.dungeon.deadends:
        dm.pruneDeadends(1)

    return dm

def level_rooms(dm):
    # generate rooms and corridors
    dm.placeRandomRooms(8, 12, 1, 1, 1000)
    x, y = dm.findEmptySpace(3)
    while x:
        dm.generateCorridors('f', x, y)
        x, y = dm.findEmptySpace(3)

    # join it all together
    dm.connectAllRooms(0)

    #clear all dead ends
    dm.findDeadends()
    while dm.dungeon.deadends:
        dm.pruneDeadends(1)

def level_generator(map_width, map_height):

    '''
    3 options:
    1) all caverns
    2) both rooms and caverns
    3) all rooms
    '''

    dm = dungeonGenerator(width=map_width, height=map_height)

    place_stair_room(dm)
    place_stair_room(dm)
    level_rooms(dm)

    return LevelMap(dm.dungeon)

    chance = randint(0,100)
    '''
    if (chance <= 33):
        dm = self.level_caverns(dm)
    elif (chance <= 66):
        dm = self.level_cavern_rooms(map_width, map_height)
    else:
        dm = self.level_rooms(map_width, map_height)
    '''

    random_lair(dm)

    place_stair_room(dm)
    place_stair_room(dm)
    '''
    self.down_stairs = Entity(dm.dungeon.rooms[-1].center_tile(), '>', 'Down Stairs',
                                tcod.silver, render_order=RenderOrder.STAIRS,
                                stairs=Stairs(self.dungeon_level + 1))

    self.up_stairs = Entity(dm.dungeon.rooms[-1].center_tile(), '<', 'Up Stairs',
                            tcod.silver, render_order=RenderOrder.STAIRS,
                            stairs=Stairs(self.dungeon_level - 1))
    '''
    dm = self.level_caverns(dm)

    return LevelMap(dm.dungeon)

def level_boss_generator(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    prefab = Prefab(boss_room())

    place_prefab(prefab, dm)

    # generate rooms and corridors
    dm.placeRandomRooms(10, 15, 2, 2, 500)

    if (prefab.door):
        dm.generateCorridors('f', prefab.door.x, prefab.door.y + 2)
        dm.dungeon.grid[prefab.door.x][prefab.door.y + 1] = Tiles.DOOR

    # join it all together
    dm.connectAllRooms(0)
    unconnected = dm.findUnconnectedAreas()
    dm.joinUnconnectedAreas(unconnected)
    dm.pruneDeadends(70)
    dm.placeWalls()
    dm.closeDeadDoors()

    return LevelMap(dm.dungeon)

def random_lair(dm):
    lair_chance = True

    if (lair_chance):
        prefab = Prefab(necromancer_lair())

        place_prefab(prefab, dm)

        #point = prefab.room.random_tile(self)
        #necro = bestiary.necromancer(point)
        #self.current_map.add_entity(necro)

def place_stair_room(dm):
    prefab = Prefab(stair_room())

    place_prefab(prefab, dm)

def place_prefab(prefab, dm):
    startX, startY = dm.placeRoomRandomly(prefab.room.width, prefab.room.height)

    prefab.room.x = startX
    prefab.room.y = startY

    dm.placeRoom(prefab.room.x, prefab.room.y, prefab.room.width, prefab.room.height)
    prefab.carve(dm.dungeon.grid)

def arena(map_width, map_height):
    dm = dungeonGenerator(width=map_width, height=map_height)

    prefab = circle_shaped_room(circle_size = 15)
    startX = (map_width // 2) - (prefab.room.width // 2)
    startY = (map_height // 2) - (prefab.room.height // 2)
    dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = False)
    prefab.room.x = startX
    prefab.room.y = startY
    prefab.carve(dm.dungeon.grid)

    for x in range(3):
        prefab = circle_shaped_room()
        startX, startY = dm.placeRoomRandomly(prefab.room.width, prefab.room.height)
        dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = False)
        prefab.room.x = startX
        prefab.room.y = startY
        prefab.carve(dm.dungeon.grid)
    '''
    for x in range(5):
        prefab = curved_side_shaped_room()
        startX, startY = dm.placeRoomRandomly(prefab.room.width, prefab.room.height)
        dm.placeRoom(startX, startY, prefab.room.width, prefab.room.height, ignoreOverlap = True)
        prefab.room.x = startX
        prefab.room.y = startY
        prefab.carve(dm.dungeon.grid)
    '''

    unconnected = dm.findUnconnectedAreas()
    dm.joinUnconnectedAreas(unconnected)

    dm.placeWalls()

    return LevelMap(dm.dungeon)

def circle_shaped_room(donut=False, circle_size = 0):

    if circle_size == 0:
        circle_size = randrange(5, 15, 2)

    floor_size = 3

    start_inset = (circle_size - floor_size) // 2
    end_inset = circle_size - start_inset - 1

    room_layout = [[i for i in range(circle_size)] for i in range(circle_size)]

    offset = 0

    for y in range(circle_size):
        for x in range(circle_size):
            if (x < (start_inset - offset)):
                room_layout[y][x] = 'E'
            elif (x > (end_inset + offset)):
                room_layout[y][x] = 'E'

        if (floor_size < circle_size):
            if y < start_inset:
                floor_size += 2
                offset += 1
            elif y > end_inset:
                floor_size -= 2
                offset -= 1
        elif (floor_size == circle_size):
            if y >= end_inset:
                floor_size -= 2
                offset -= 1

    if donut:
        pass

    #print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in room_layout]))

    prefab = Prefab(room_layout)

    return prefab

def curved_side_shaped_room():

    corner_to_round = randint(1,2)

    top_left = False
    top_right = False
    bottom_left = False
    bottom_right = False

    min_height = 7
    max_height = 15
    min_width = 7
    max_height = 15

    if corner_to_round == 1:
        top_left = True
    elif corner_to_round == 2:
        top_right = True
    elif corner_to_round == 3:
        bottom_left = True
    elif corner_to_round == 4:
        bottom_right = True

    floor_size = 2

    height = randrange(min_height, max_height, 2)
    width = randrange(min_height, max_height, 2)

    room_layout = [[i for i in range(width)] for i in range(height)]

    start_inset = width - floor_size
    end_inset = width - start_inset

    offset = 0

    print("Start inset: " + str(start_inset))
    print("End inset: " + str(end_inset))
    for y in range(height):
        for x in range(width):
            if (top_left or bottom_left) and (x < (start_inset - offset)):
                room_layout[y][x] = 'E'
            elif (top_right or bottom_right) and (x > (end_inset + offset)):
                room_layout[y][x] = 'E'

        if (floor_size < width):
            if y < start_inset:
                floor_size += 1
                offset += 1
            elif y >= (start_inset + floor_size):
                floor_size -= 1
                offset -= 1
        elif (floor_size == width):
            pass
            #if y >= end_inset:
            #    floor_size -= 2
            #    offset -= 1

    print('===================================================')
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in room_layout]))

    prefab = Prefab(room_layout)

    return prefab
'''
import numpy as np
m = np.array([[1,2,3],
     [2,3,3],
     [5,4,3]])

def rotate_matrix(mat):
return np.rot90(mat)
'''
