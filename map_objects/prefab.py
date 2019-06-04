from etc.enum import Tiles
from utils.utils import matprint
import numpy as np


def boss_room():
    room_map = ["vvv##S##vvv",
                "vv##...##vv",
                "v##.....##v",
                "##.......##",
                "...........",
                "...........",
                "..#.....#..",
                "...........",
                "..#.....#..",
                "...........",
                "..#.....#..",
                "...........",
                "..#.....#..",
                "...........",
                "..#.....#..",
                "vvvvvDvvvvv"]

    return room_map
'''
def necromancer_lair():
    room_map = ["#####.#####",
                "####...####",
                "###.....###",
                "##.......##",
                "#....W....#",
                "....WWW....",
                "#....W....#",
                "##.......##",
                "###.....###",
                "####...####",
                "#####.#####"]
'''

def stair_room():
    room_map = ["VDV",
                "...",
                ".S.",
                "..."]

    return room_map

def necromancer_lair():
    room_map = ["...........",
                "...........",
                ".....W.....",
                "....WWW....",
                ".....W.....",
                "...........",
                "..........."]

    return room_map

def barracks():
    room_map = [".........",
                ".........",
                ".........",
                ".........",
                ".........",
                "####.####",
                "...#.#...",
                ".........",
                "...#.#...",
                "####.####",
                "...#.#...",
                ".........",
                "...#.#...",
                "####.####",
                "...#.#...",
                ".........",
                "...#.#...",
                "####.####",
                "...#.#...",
                ".........",
                "...#.#...",
                "VVVVDVVVV"]

    return room_map

def make_room_slice(room_map):
    grid = np.zeros((len(room_map), len(room_map[0])), dtype=np.int8)

    for x in range(0, len(room_map)):
        for y in range(0, len(room_map[0])):
            try:
                if (room_map[x][y] == "#"):
                    grid[x,y] = Tiles.ROOM_WALL
                elif (room_map[x][y] == "I"):
                    grid[x,y] = Tiles.IMPENETRABLE
                elif (room_map[x][y] == "E"):
                    grid[x,y] = Tiles.EMPTY
                elif (room_map[x][y] == "W"):
                    grid[x,y] = Tiles.SHALLOWWATER
                elif (room_map[x][y] == "S"):
                    grid[x,y] = Tiles.STAIRSFLOOR
                elif (room_map[x][y] == "D"):
                    grid[x,y] = Tiles.DOOR
                elif (room_map[x][y] == "V"):
                    grid[x,y] = Tiles.EMPTY
                else:
                    grid[x,y] = Tiles.ROOM_FLOOR
            except IndexError:
                print(str(x) + " " + str(y))

    matprint(grid)

    return grid
