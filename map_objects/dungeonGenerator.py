##################################################################
#                                                                #
# Procedural Dungeon Generator v1.1                              #
#                                                                #
# By Jay (Battery)                                               #
#                                                                #
# https://whatjaysaid.wordpress.com/                             #
# for how use it got to:                                         #
# https://whatjaysaid.wordpress.com/2016/01/15/1228              #
#                                                                #
# Feel free to use this as you wish, but please keep this header #
#                                                                #
##################################################################

import tcod as libtcod

from enum import IntEnum, auto
from random import randint, choice, randrange

from map_objects.dungeon import Dungeon
from map_objects.point import Point

#tile constants
from etc.enum import Tiles

floor_to_wall = {
    Tiles.OBSTACLE: Tiles.CAVERN_WALL,
    Tiles.IMPENETRABLE: Tiles.CAVERN_WALL,
    Tiles.CAVERN_FLOOR: Tiles.CAVERN_WALL,
    Tiles.DEADEND: Tiles.CORRIDOR_WALL,
    Tiles.CORRIDOR_FLOOR: Tiles.CORRIDOR_WALL,
    Tiles.ROOM_FLOOR: Tiles.ROOM_WALL,
    Tiles.DEEPWATER: Tiles.CAVERN_WALL,
    Tiles.SHALLOWWATER: Tiles.CAVERN_WALL
}

class Prefab:
    def __init__(self, room_map):
        self.room_map = room_map
        self.room = None
        self.layout = []
        self.door = None

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

        self.room = dungeonRoom(0,0,len(self.room_map[0]),len(self.room_map))

    def carve(self, map):
        for xoffset in range(0, self.room.width):
            for yoffset in range(0, self.room.height):
                if (self.layout[xoffset][yoffset] == "#"):
                    map[self.room.x + xoffset][self.room.y + yoffset] = Tiles.ROOM_WALL
                elif (self.layout[xoffset][yoffset] == "I"):
                    map[self.room.x + xoffset][self.room.y + yoffset] = Tiles.IMPENETRABLE
                elif (self.layout[xoffset][yoffset] == "W"):
                    map[self.room.x + xoffset][self.room.y + yoffset] = Tiles.SHALLOWWATER
                elif (self.layout[xoffset][yoffset] == "D"):
                    map[self.room.x + xoffset][self.room.y + yoffset] = Tiles.ROOM_FLOOR
                    self.door = Point(self.room.x + xoffset, self.room.y + yoffset)
                else:
                    map[self.room.x + xoffset][self.room.y + yoffset] = Tiles.ROOM_FLOOR

class dungeonRoom:
    """
    a simple container for dungeon rooms
    since you may want to return to constructing a room, edit it, etc. it helps to have some way to save them
    without having to search through the whole game grid

    Args:
        x and y coodinates for the room
        width and height for the room

    Attributes:
        x, y: the starting coordinates in the 2d array
        width: the ammount of cells the room spans
        height: the ammount of cells the room spans
    """

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def describe(self):
        return "Room: " + str(self.x) + ',' + str(self.y) + ',' + str(self.width) + ',' + str(self.height)

    def random_tile(self, map):
        point = None
        while (point == None):
            x = libtcod.random_get_int(None, self.x + 1, self.x + self.width - 2)
            y = libtcod.random_get_int(None, self.y + 1, self.y + self.height - 2)

            if not map.current_level.blocked[x, y]:
                point = Point(x,y)

        return point

    def center_tile(self):
        point = Point(self.x + int(self.width / 2), int(self.y + self.height / 2))

        return point

class dungeonGenerator:
    """
    A renderer/framework/engine independent functions for generating random dungeons, including rooms, corridors, connects and path finding

    The dungeon is built around a 2D list, the resulting dungeon is a 2D tile map, where each x,y point holds a
    constant. The grid can then be iterated through using the contained constant to determine the tile to render and the x,y indice can be
    multiplied by x,y size of the tile. The class it's self can be iterated through. For example:

        tileSize = 2
        for x, y, tile in dungeonGenerator:
            if tile = FLOOR:
                render(floorTile)
                floorTile.xPosition = x * tileSize
                floorTile.yPosition = y * tileSize
            and so forth...

    Alternatively:

        for x in range(dungeonGenerator.width):
            for y in range(dungeonGenerator.height):
                if dungeonGenerator.grid[x][y] = FLOOR:
                    render(floorTile)
                    floorTile.xPosition = x * tileSize
                    floorTile.yPosition = y * tileSize
                and so forth...


    Throughout x,y refer to indicies in the tile map, nx,ny are used to refer to neighbours of x,y

    Args:
        height and width of the dungeon to be generated

    Attributes:
        width: size of the dungeon in the x dimension
        height: size of the dungeon in the y dimension
        grid: a 2D list (grid[x][y]) for storing tile constants (read tile map)
        rooms: **list of all the dungeonRoom objects in the dungeon, empty until placeRandomRooms() is called
        doors: **list of all grid coordinates of the corridor to room connections, elements are tuples (x,y), empty until connectAllRooms() is called
        corridors: **list of all the corridor tiles in the grid, elements are tuples (x,y), empty until generateCorridors() is called
        deadends: list of all corridor tiles only connected to one other tile, elements are tuples (x,y), empty until findDeadends() is called
        graph: dictionary where keys are the coordinates of all floor/corridor tiles and values are a list of floor/corridor directly connected, ie (x, y): [(x+1, y), (x-1, y), (x, y+1), (x, y-1)], empty until constructGraph() is called
        caves: list of all the floor tiles in areas generated with generateCaves
        alcoves: list of all the alcoves (a floor tile with 3 wall tiles adjoining) in the cave areas
        ** once created these will not be re-instanced, therefore any user made changes to grid will also need to update these lists for them to remain valid
    """

    def __init__(self, width, height):
        self.dungeon = Dungeon(width, height)

    def __iter__(self):
        for xi in range(self.dungeon.width):
            for yi in range(self.dungeon.height):
                yield xi, yi, self.dungeon.grid[xi][yi]

    ##### HELPER FUNCTIONS #####

    def findNeighbours(self, x, y):
        """
        finds all cells that touch a cell in a 2D grid

        Args:
            x and y: integer, indicies for the cell to search around

        Returns:
            returns a generator object with the x,y indicies of cell neighbours
        """

        xi = (0, -1, 1) if 0 < x < self.dungeon.width - 1 else ((0, -1) if x > 0 else (0, 1))
        yi = (0, -1, 1) if 0 < y < self.dungeon.height - 1 else ((0, -1) if y > 0 else (0, 1))
        for a in xi:
            for b in yi:
                if a == b == 0:
                    continue
                yield (x+a, y+b)

    def findNeighboursDirect(self, x, y):
        """
        finds all neighbours of a cell that directly touch it (up, down, left, right) in a 2D grid

        Args:
            x and y: integer, indicies for the cell to search around

        Returns:
            returns a generator object with the x,y indicies of cell neighbours
        """
        xi = (0, -1, 1) if 0 < x < self.dungeon.width - 1 else ((0, -1) if x > 0 else (0, 1))
        yi = (0, -1, 1) if 0 < y < self.dungeon.height - 1 else ((0, -1) if y > 0 else (0, 1))
        for a in xi:
            for b in yi:
                if abs(a) == abs(b):
                    continue
                yield (x+a, y+b)

    def canCarve(self, x, y, xd, yd):
        """
        checks to see if a path can move in certain direction, used by getPossibleMoves()

        Args:
            x and y: integer, indicies in the 2D grid of the starting cell
            xd and xy: integer, direction trying to move in where (-1,0) = left, (1,0) = right, (0,1) = up, (0,-1) = down

        Returns:
            True if it is safe to move that way
        """

        xi = (-1, 0, 1) if not xd else (1*xd, 2*xd)
        yi = (-1, 0, 1) if not yd else (1*yd, 2*yd)
        for a in xi:
            for b in yi:
                if self.dungeon.grid[a+x][b+y]:
                    return False
        return True

    def getPossibleMoves(self, x, y):
        """
        searchs for potential directions that a corridor can expand in
        used by generatePath()

        Args:
            x and y: integer, indicies of the tile on grid to find potential moves (up, down, left, right) for

        Returns:
            a list of potential x,y coords that the path could move it, each entry stored as a tuple
        """

        availableSquares = []
        for nx, ny in self.findNeighboursDirect(x, y):
            if nx < 1 or ny < 1 or nx > self.dungeon.width-2 or ny > self.dungeon.height-2: continue
            xd = nx - x
            yd = ny - y
            if self.canCarve(x, y, xd, yd):
                availableSquares.append((nx, ny))
        return availableSquares

    def quadFits(self, sx, sy, rx, ry, margin):
        """
        looks to see if a quad shape will fit in the grid without colliding with any other tiles
        used by placeRoom() and placeRandomRooms()

        Args:
            sx and sy: integer, the bottom left coords of the quad to check
            rx and ry: integer, the width and height of the quad, where rx > sx and ry > sy
            margin: integer, the space in grid cells (ie, 0 = no cells, 1 = 1 cell, 2 = 2 cells) to be away from other tiles on the grid

        returns:
            True if the quad fits
        """

        sx -= margin
        sy -= margin
        rx += margin*2
        ry += margin*2
        if sx + rx < self.dungeon.width and sy + ry < self.dungeon.height and sx >= 0 and sy >= 0:
            for x in range(rx):
                for y in range(ry):
                    if self.dungeon.grid[sx+x][sy+y]:
                        return False
            return True
        return False

    def floodFill(self, x, y, fillWith, tilesToFill = [], grid = None):
        """
        Fills tiles connected to the starting tile
        passing the same fillWith value as the starting tile value will produce no results since they're already filled

        Args:
            x and y: integers, the grid coords to star the flood fill, all filled tiles will be connected to this tile
            fillWith: integer, the constant of the tile to fill with
            tilesToFill: list of integers, allows you to control what tile get filled, all if left out
            grid: list[[]], a 2D array to flood fill, by default this is dungeonGenerator.grid, however if you do not want to overwrite this you can provide your own 2D array (such as a deep copy of dungeonGenerator.grid)

        Returns:
            none
        """
        if not grid: grid = self.dungeon.grid
        toFill = set()
        toFill.add((x,y))
        count = 0
        while toFill:
            x, y = toFill.pop()
            if tilesToFill and grid[x][y] not in tilesToFill: continue
            if not grid[x][y]: continue
            grid[x][y] = fillWith
            for nx, ny in self.findNeighboursDirect(x, y):
                if grid[nx][ny] != fillWith:
                    toFill.add((nx, ny))
            count += 1
            if count > self.dungeon.width * self.dungeon.height:
                print('overrun')
                break


    ##### LEVEL SEARCH FUNCTIONS #####

    def findEmptySpace(self, distance):
        """
        Finds the first empty space encountered in the 2D grid that it not surrounding by anything within the given distance

        Args:
            distance: integer, the distance from the current x,y point being checked to see if is empty

        Returns:
            the x,y indicies of the free space or None, None if no space was found
        """

        for x in range(distance, self.dungeon.width - distance):
            for y in range(distance, self.dungeon.height - distance):
                touching = 0
                for xi in range(-distance, distance):
                    for yi in range(-distance, distance):
                        if self.dungeon.grid[x+xi][y+yi]: touching += 1
                if not touching:
                    return x, y
        return None, None

    def findUnconnectedAreas(self):
        """
        Checks through the grid to find islands/unconnected rooms
        Note, this can be slow for large grids and memory intensive since it needs to create a deep copy of the grid
        in order to use joinUnconnectedAreas() this needs to be called first and the returned list passed to joinUnconnectedAreas()

        Args:
            none

        Returns:
            A list of unconnected cells, where each group of cells is in its own list and each cell indice is stored as a tuple, ie [[(x1,y1), (x2,y2), (x3,y3)], [(xi1,yi1), (xi2,yi2), (xi3,yi3)]]
        """
        unconnectedAreas = []
        areaCount = 0
        gridCopy = [[Tiles.EMPTY for i in range(self.dungeon.height)] for i in range(self.dungeon.width)]
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                if self.dungeon.grid[x][y]:
                    gridCopy[x][y] = 'x'
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                if gridCopy[x][y] == 'x':
                    unconnectedAreas.append([])
                    areaCount += 1
                    self.floodFill(x, y, areaCount, None, gridCopy)
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                if gridCopy[x][y]:
                    i = gridCopy[x][y]
                    unconnectedAreas[i-1].append((x,y))
        return unconnectedAreas

    def findDeadends(self):
        """
        looks through all the corridors generated by generatePath() and joinUnconnectedAreas() to identify dead ends
        populates self.dungeon.deadends and is used by pruneDeadends()

        Args:
            none
        Returns:
            none
        """

        self.dungeon.deadends = []
        for x, y in self.dungeon.corridors:
            touching = 0
            for nx, ny in self.findNeighboursDirect(x,y):
                if self.dungeon.grid[nx][ny]: touching += 1
            if touching == 1: self.dungeon.deadends.append((x,y))

    def findAlcoves(self):
        self.dungeon.alcoves = []
        for xi in range(self.dungeon.width):
            for yi in range(self.dungeon.height):
                walls = 0
                if (self.dungeon.grid[xi][yi] == Tiles.CAVERN_FLOOR):
                    for nx, ny in self.findNeighboursDirect(xi, yi):
                        if (self.dungeon.grid[nx][ny] <= Tiles.ROOM_WALL):
                            walls += 1
                    if (walls == 3):
                        self.dungeon.alcoves.append(Point(xi, yi))

    def findCaves(self):
        self.dungeon.caves = []
        for xi in range(self.dungeon.width):
            for yi in range(self.dungeon.height):
                if (self.dungeon.grid[xi][yi] == Tiles.CAVERN_FLOOR):
                    self.dungeon.caves.append(Point(xi, yi))

    ##### GENERATION FUNCTIONS #####

    def placeRoom(self, startX, startY, roomWidth, roomHeight, ignoreOverlap = False):
        """
        place a defined quad within the grid and add it to self.dungeon.rooms

        Args:
            x and y: integer, starting corner of the room, grid indicies
            roomWdith and roomHeight: integer, height and width of the room where roomWidth > x and roomHeight > y
            ignoreOverlap: boolean, if true the room will be placed irregardless of if it overlaps with any other tile in the grid
                note, if true then it is up to you to ensure the room is within the bounds of the grid

        Returns:
            True if the room was placed
        """

        if self.quadFits(startX, startY, roomWidth, roomHeight, 0) or ignoreOverlap:
            for x in range(roomWidth):
                for y in range(roomHeight):
                    self.dungeon.grid[startX+x][startY+y] = Tiles.ROOM_FLOOR
            self.dungeon.rooms.append(dungeonRoom(startX, startY, roomWidth, roomHeight))
            return True

    def placeRandomRooms(self, minRoomSize, maxRoomSize, roomStep = 1, margin = 1, attempts = 500):
        """
        randomly places quads in the grid
        takes a brute force approach: randomly a generate quad in a random place -> check if fits -> reject if not
        Populates self.dungeon.rooms

        Args:
            minRoomSize: integer, smallest size of the quad
            maxRoomSize: integer, largest the quad can be
            roomStep: integer, the amount the room size can grow by, so to get rooms of odd or even numbered sizes set roomSize to 2 and the minSize to odd/even number accordingly
            margin: integer, space in grid cells the room needs to be away from other tiles
            attempts: the amount of tries to place rooms, larger values will give denser room placements, but slower generation times

        Returns:
            none
        """

        for attempt in range(attempts):
            roomWidth = randrange(minRoomSize, maxRoomSize, roomStep)
            roomHeight = randrange(minRoomSize, maxRoomSize, roomStep)
            startX = randint(0, self.dungeon.width)
            startY = randint(0, self.dungeon.height)
            if self.quadFits(startX, startY, roomWidth, roomHeight, margin):
                for x in range(roomWidth):
                    for y in range(roomHeight):
                        self.dungeon.grid[startX+x][startY+y] = Tiles.ROOM_FLOOR
                self.dungeon.rooms.append(dungeonRoom(startX, startY, roomWidth, roomHeight))

    def generateCaves(self, p = 45, smoothing = 4):
        """
        Generates more organic shapes using cellular automata

        Args:
            p: the probability that a cell will become a cave section, values between 30 and 45 work well
            smoothing: amount of noise reduction, lower values produce more jagged caves, little effect past 4

        Returns:
            None
        """

        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                if randint(0, 100) < p:
                    self.dungeon.grid[x][y] = Tiles.CAVERN_FLOOR
        for i in range(smoothing):
            for x in range(self.dungeon.width):
                for y in range(self.dungeon.height):
                    if x == 0 or x == self.dungeon.width or y == 0 or y == self.dungeon.height:
                        self.dungeon.grid[x][y] = Tiles.EMPTY
                    touchingEmptySpace = 0
                    for nx, ny in self.findNeighbours(x,y):
                        if self.dungeon.grid[nx][ny] == Tiles.CAVERN_FLOOR:
                            touchingEmptySpace += 1
                    if touchingEmptySpace >= 5:
                        self.dungeon.grid[x][y] = Tiles.CAVERN_FLOOR
                    elif touchingEmptySpace <= 2:
                       self.dungeon.grid[x][y] = Tiles.EMPTY

    def generateCorridors(self, mode = 'r', x = None, y = None):
        """
        generates a maze of corridors on the growing tree algorithm,
        where corridors do not overlap with over tiles, are 1 tile away from anything else and there are no diagonals
        Populates self.dungeon.corridors

        Args:
            mode: char, either 'r', 'f', 'm' or 'l'
                  this controls how the next tile to attempt to move to is determined and affects how the generated corridors look
                  'r' - random selection, produces short straigh sections with spine like off-shoots, lots of deadends
                  'f' - first cell in the list to check, long straight secions and few diagnol snaking sections
                  'm' - similar to first but more likely to snake
                  'l' - snaking and winding corridor sections
            x and y: integer, grid indicies, starting point for the corridor generation,
                     if none is provided a random one will be chosen

            Returns:
                none
        """

        cells = []
        if not x and not y:
            x = randint(1, self.dungeon.width-2)
            y = randint(1, self.dungeon.height-2)
            while not self.dungeon.canCarve(x, y, 0, 0):
                x = randint(1, self.dungeon.width-2)
                y = randint(1, self.dungeon.height-2)
        self.dungeon.grid[x][y] = Tiles.CORRIDOR_FLOOR
        self.dungeon.corridors.append((x,y))
        cells.append((x,y))
        while cells:
            if mode == 'l':
                x, y = cells[-1]
            elif mode == 'r':
                x, y = choice(cells)
            elif mode == 'f':
                x, y = cells[0]
            elif mode == 'm':
                x, y = cells[len(cells)//2]
            possMoves = self.getPossibleMoves(x, y)
            if possMoves:
                xi, yi = choice(possMoves)
                self.dungeon.grid[xi][yi] = Tiles.CORRIDOR_FLOOR
                self.dungeon.corridors.append((xi,yi))
                cells.append((xi, yi))
            else:
                cells.remove((x, y))

    def pruneDeadends(self, amount):
        """
        Removes deadends from the corridors/maze
        each iteration will remove all identified dead ends
        it will update self.dungeon.deadEnds after

        Args:
            amount: number of iterations to remove dead ends

        Returns:
            none
        """
        for i in range(amount):
            self.findDeadends()
            for x, y in self.dungeon.deadends:
                self.dungeon.grid[x][y] = Tiles.EMPTY
                self.dungeon.corridors.remove((x,y))
        self.findDeadends()

    def placeWalls(self):
        """
        Places wall tiles around all floor, door and corridor tiles
        As some functions (like floodFill() and anything that uses it) dont distinguish between tile types it is best called later/last

        Args:
            none

        Returns:
            none
        """

        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                wallType = floor_to_wall.get(self.dungeon.grid[x][y])
                if not wallType:
                    continue

                for nx, ny in self.findNeighbours(x,y):
                    if not self.dungeon.grid[nx][ny] or (wallType > self.dungeon.grid[nx][ny]):
                        self.dungeon.grid[nx][ny] = wallType

    def connectAllRooms(self, extraDoorChance = 0):
        """
        Joins rooms to the corridors
        This not gauranteed to join everything,
        depending on how rooms are placed and corridors generated it is possible to have unreachable rooms
        in that case joinUnconnectedAreas() can join them
        Populates self.dungeon.doors

        Args:
            extraDoorChance: integer, where 0 >= extraDoorChance <= 100, the chance a room will have more than one connection to the corridors
        if extraDoorChance >= 100: extraDoorChance = 99

        Returns:
            list of dungeonRoom's that are not connected, this will not include islands, so 2 rooms connected to each other, but not the rest will not be included
        """

        unconnectedRooms = []
        for room in self.dungeon.rooms:
            connections = []
            for i in range(room.width):
                if self.dungeon.grid[room.x+i][room.y-2]:
                    connections.append((room.x+i, room.y-1))
                if room.y+room.height+1 < self.dungeon.height and self.dungeon.grid[room.x+i][room.y+room.height+1]:
                    connections.append((room.x+i, room.y+room.height))
            for i in range(room.height):
                if self.dungeon.grid[room.x-2][room.y+i]:
                    connections.append((room.x-1, room.y+i))
                if room.x+room.width+1 < self.dungeon.width and self.dungeon.grid[room.x+room.width+1][room.y+i]:
                    connections.append((room.x+room.width, room.y+i))
            if connections:
                chance = -1
                while chance <= extraDoorChance:
                    pickAgain = True
                    while pickAgain:
                        x, y = choice(connections)
                        pickAgain = False
                        for xi, yi in self.findNeighbours(x, y):
                            if self.dungeon.grid[xi][yi] == Tiles.DOOR:
                                pickAgain = True
                                break
                    chance = randint(0, 100)
                    self.dungeon.grid[x][y] = Tiles.DOOR
                    self.dungeon.doors.append((x, y))
            else:
                unconnectedRooms.append(room)
        return unconnectedRooms

    def joinUnconnectedAreas(self, unconnectedAreas):
        """
        Forcibly connect areas not joined together
        This will work nearly every time (I've seen one test case where an area was still unjoined)
        But it will not always produce pretty results - connecting paths may cause diagonal touching

        Args:
            unconnectedAreas: the list returned by findUnconnectedAreas() - ie [[(x1,y1), (x2,y2), (x3,y3)], [(xi1,yi1), (xi2,yi2), (xi3,yi3)]]

        Returns:
            none
        """
        connections = []
        while len(unconnectedAreas) >= 2:
            bestDistance = self.dungeon.width + self.dungeon.height
            c = [None, None]
            toConnect = unconnectedAreas.pop()
            for area in unconnectedAreas:
                for x, y in area:
                    for xi, yi in toConnect:
                        distance = abs(x-xi) + abs(y-yi)
                        if distance < bestDistance and (x == xi or y == yi):
                            bestDistance = distance
                            c[0] = (x,y)
                            c[1] = (xi,yi)
            c.sort()
            x, y = c[0]
            for x in range(c[0][0]+1, c[1][0]):
                if self.dungeon.grid[x][y] == Tiles.EMPTY:
                    self.dungeon.grid[x][y] = Tiles.CORRIDOR_FLOOR
            for y in range(c[0][1]+1, c[1][1]):
                if self.dungeon.grid[x][y] == Tiles.EMPTY:
                    self.dungeon.grid[x][y] = Tiles.CORRIDOR_FLOOR
            self.dungeon.corridors.append((x,y))

    def closeDeadDoors(self):
        """
        Remove any doors that don't have either a floor tile E & W or N & S and
        walls (or empty tiles) on the opposite axis and replace with a corridor.

        Args:
            none

        Returns:
            none
        """
        for xi in range(self.dungeon.width):
            for yi in range(self.dungeon.height):
                if (self.dungeon.grid[xi][yi] == Tiles.DOOR):
                    north_wall = False
                    north_floor = False

                    south_wall = False
                    south_floor = False

                    east_wall = False
                    east_floor = False

                    west_wall = False
                    west_floor = False

                    if (xi == 0) or (self.dungeon.grid[xi - 1][yi] in [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL]):
                        west_wall = True
                    elif (self.dungeon.grid[xi - 1][yi] in [Tiles.CAVERN_FLOOR, Tiles.CORRIDOR_FLOOR, Tiles.ROOM_FLOOR]):
                        west_floor = True

                    if (xi == self.dungeon.width) or (self.dungeon.grid[xi + 1][yi] in [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL]):
                        east_wall = True
                    elif (self.dungeon.grid[xi + 1][yi] in [Tiles.CAVERN_FLOOR, Tiles.CORRIDOR_FLOOR, Tiles.ROOM_FLOOR]):
                        east_floor = True

                    if (yi == 0) or (self.dungeon.grid[xi][yi - 1] in [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL]):
                        north_wall = True
                    elif (self.dungeon.grid[xi][yi - 1] in [Tiles.CAVERN_FLOOR, Tiles.CORRIDOR_FLOOR, Tiles.ROOM_FLOOR]):
                        north_floor = True

                    if (yi == self.dungeon.height) or (self.dungeon.grid[xi][yi + 1] in [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL]):
                        south_wall = True
                    elif (self.dungeon.grid[xi][yi + 1] in [Tiles.CAVERN_FLOOR, Tiles.CORRIDOR_FLOOR, Tiles.ROOM_FLOOR]):
                        south_floor = True

                    if (north_wall and south_wall and west_floor and east_floor):
                        continue

                    if (north_floor and south_floor and west_wall and east_wall):
                        continue

                    self.dungeon.grid[xi][yi] = Tiles.CORRIDOR_FLOOR

    ##### PATH FINDING FUNCTIONS #####

    def constructNavGraph(self):
        """
        builds the navigation grapth for path finding
        must be called before findPath()
        Populates self.dungeon.graph

        Args:
            none

        Returns:
            none
        """
        for x, y in self.dungeon.corridors:
            if self.dungeon.grid[x][y] <= Tiles.ROOM_WALL: break
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                if self.dungeon.grid[x][y] > Tiles.ROOM_WALL:
                    self.dungeon.graph[(x, y)] = []
                    for nx, ny in self.findNeighboursDirect(x, y):
                        if self.dungeon.grid[nx][ny] > Tiles.ROOM_WALL:
                            self.dungeon.graph[(x, y)].append((nx, ny))

    def findPath(self, startX, startY, endX, endY):
        """
        finds a path between 2 points on the grid
        While not part of generating a dungeon/level it was included as I initially thought that
        since the generator had lots of knowledge about the maze it could use that for fast path finding
        however, the overhead of any heuristic was always greater than time saved. But I kept this as its useful

        Args:
            startX, startY: integers, grid indicies to find a path from
            endY, endY: integers, grid indicies to find a path to

        Returns:
            a list of grid cells (x,y) leading from the end point to the start point
            such that [(endX, endY) .... (startY, endY)] to support popping of the end as the agent moves
        """

        cells = []
        cameFrom = {}
        cells.append((startX, startY))
        cameFrom[(startX, startY)] = None
        while cells:
            # manhattan distance sort, commented out at slow, but there should you want it
            #cells.sort(key=lambda x: abs(endX-x[0]) + abs(endY - x[1]))
            current = cells[0]
            del cells[0]
            if current == (endX, endY):
                break
            for nx, ny in self.dungeon.graph[current]:
                if (nx, ny) not in cameFrom:
                    cells.append((nx, ny))
                    cameFrom[(nx, ny)] = current
        if (endX, endY) in cameFrom:
            path = []
            current = (endX, endY)
            path.append(current)
            while current != (startX, startY):
                current = cameFrom[current]
                path.append(current)
            return path
