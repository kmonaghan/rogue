import game_state

from map_objects.room import Room

def boss_room():
    room_map = ["###...###",
                "##.....##",
                "#.......#",
                ".........",
                "..#...#..",
                ".........",
                "..#...#..",
                ".........",
                "..#...#..",
                "........."]

    return room_map

class Prefab:
    def __init__(self, room_map):
        self.room_map = room_map
        self.room = None
        self.layout = []

        self.parse_map()

    def parse_map(self):
        self.layout = [["#"
        			for y in range(len(self.room_map))]
        				for x in range(len(self.room_map[0]))]
        y = 0
        for line in self.room_map:
            x = 0
            for tile in line:
                self.layout[x][y] = tile
                x += 1
            y += 1

        self.room = Room(0,0,x,y)

        if (game_state.debug):
            print "Prefabbed " + self.room.describe()

    def carve(self, map):
        for xoffset in range(0, self.room.w):
            for yoffset in range(0, self.room.h):
                if (self.layout[xoffset][yoffset] == "#"):
                    map[self.room.x1 + xoffset][self.room.y1 + yoffset].setWall()
                else:
                    map[self.room.x1 + xoffset][self.room.y1 + yoffset].setFloor()
