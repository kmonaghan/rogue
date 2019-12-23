from etc.enum import Tiles
from utils.utils import matprint
import numpy as np

def boss_room(top = 1, middle = 1, bottom = 1):
    room_map = ["vvvvv###vvvvv",
                "vvvv##S##vvvv",
                "vvv##...##vvv",
                "vv##.....##vv",
                "v##.......##v",
                "#...........#",
                "#...........#",
                "#..#.....#..#",
                "#...........#",
                "#..#.....#..#",
                "#...........#",
                "#..#.....#..#",
                "#...........#",
                "#..#.....#..#",
                "#...........#",
                "#..#.....#..#",
                "######D######"]

    return room_map

def stair_room(top = 1, middle = 1, bottom = 1):
    room_map = ["##D##",
                "#...#",
                "#.X.#",
                "#...#",
                "#####"]

    return room_map

def treasure_room(top = 1, middle = 1, bottom = 1):
    room_map = ["V##E##V",
                "##...##",
                "#.....#",
                "##...##",
                "V##S##V",
                "VV###VV"]

    return room_map

def necromancer_lair(top = 1, middle = 1, bottom = 1):
    room_map = ["v#########v",
                "##...S...##",
                "#....W....#",
                "#...WWW...#",
                "#....W....#",
                "##.......##",
                "v####E####v"]

    return room_map

def prison_block(top = 1, middle = 1, bottom = 1):
    room_map = []

    for x in range(top):
        room_map.append("VV#######VV")
        room_map.append("VV#..S..#VV")
        room_map.append("VV#.....#VV")
        room_map.append("#####D#####")
    for x in range(middle):
        room_map.append("#S..D.D..S#")
        room_map.append("#####.#####")
    for x in range(bottom):
        room_map.append("V#.......#V")
        room_map.append("V#.......#V")
        room_map.append("V#.......#V")
        room_map.append("V####E####V")

    return room_map

def barracks(top = 1, middle = 1, bottom = 1):
    room_map = []

    for x in range(top):
        room_map.append("V#########V")
        room_map.append("V#.......#V")
        room_map.append("V#...S...#V")
        room_map.append("V#.......#V")

    for x in range(middle):
        room_map.append("#####.#####")
        room_map.append("#...#.#...#")
        room_map.append("#...D.D...#")
        room_map.append("#...#.#...#")

    room_map.append("#####E#####")

    return room_map

list_of_prefabs = [treasure_room,
                    necromancer_lair,
                    prison_block,
                    barracks]
