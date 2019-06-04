from math import sqrt
import numpy as np
import operator
from random import choice, randint, randrange

import tcod

#tile constants
from etc.enum import Tiles, WALKABLE_TILES, BLOCKING_TILES

floor_to_wall = {
    Tiles.OBSTACLE: Tiles.CAVERN_WALL,
    Tiles.IMPENETRABLE: Tiles.CAVERN_WALL,
    Tiles.CAVERN_FLOOR: Tiles.CAVERN_WALL,
    Tiles.DEADEND: Tiles.CORRIDOR_WALL,
    Tiles.CORRIDOR_FLOOR: Tiles.CORRIDOR_WALL,
    Tiles.ROOM_FLOOR: Tiles.ROOM_WALL,
    Tiles.ROOM_WALL: Tiles.ROOM_WALL,
    Tiles.STAIRSFLOOR: Tiles.ROOM_WALL,
    Tiles.DEEPWATER: Tiles.CAVERN_WALL,
    Tiles.SHALLOWWATER: Tiles.CAVERN_WALL,
    Tiles.DOOR: Tiles.ROOM_WALL,
}

from utils.utils import matprint

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

    def __init__(self, x, y, slice):
        self.x = x
        self.y = y
        self.slice = slice

    def __str__(self):
        return f"{self.x},{self.y} {self.slice.shape}"

    def __repr__(self):
        return f"{self.x},{self.y} {self.slice.shape}"

    @property
    def width(self):
        return self.slice.shape[0]

    @property
    def height(self):
        return self.slice.shape[0]

class dungeonGenerator:
    def __init__(self, width, height):
        self.grid = np.zeros((width, height), dtype=np.int8)

        self.grid[0] = Tiles.IMPENETRABLE
        self.grid[-1] = Tiles.IMPENETRABLE
        self.grid[:, 0] = Tiles.IMPENETRABLE
        self.grid[:, -1] = Tiles.IMPENETRABLE

        self.rooms = []

    @property
    def width(self):
        return self.grid.shape[0]

    @property
    def height(self):
        return self.grid.shape[0]

    def quadFits(self, sx, sy, rx, ry, margin):
        top_x = sx-margin
        if top_x < 0:
            top_x = 0
        top_y = sy-margin
        if top_y < 0:
            top_y = 0

        bottom_x = sx+rx+margin
        if bottom_x > (self.grid.shape[0] - 1):
            bottom_x = self.grid.shape[0] - 1
        bottom_y = sy+ry+margin
        if bottom_y > (self.grid.shape[1] - 1):
            bottom_y = self.grid.shape[1] - 1

        room_bounds = self.grid[top_x:bottom_x, top_y:bottom_y]

        if np.count_nonzero(room_bounds) > 0:
            print("Another feature is too close.")
            return False

        return True

    def findNeighboursDirect(self, x, y, moves_grid):
        """
        finds all neighbours of a cell that directly touch it (up, down, left, right) in a 2D grid

        Args:
            x and y: integer, indicies for the cell to search around

        Returns:
            returns a generator object with the x,y indicies of cell neighbours
        """
        xi = (0, -1, 1) if 0 < x < moves_grid.shape[0] - 1 else ((0, -1) if x > 0 else (0, 1))
        yi = (0, -1, 1) if 0 < y < moves_grid.shape[1] - 1 else ((0, -1) if y > 0 else (0, 1))
        for a in xi:
            for b in yi:
                if abs(a) == abs(b):
                    continue
                yield (x+a, y+b)

    def getPossibleMoves(self, x, y, exclude_x = None, exclude_y = None, moves_grid = None, check_carve = True):
        """
        searchs for potential directions that a corridor can expand in
        used by generatePath()

        Args:
            x and y: integer, indicies of the tile on grid to find potential moves (up, down, left, right) for

        Returns:
            a list of potential x,y coords that the path could move it, each entry stored as a tuple
        """

        if moves_grid is None:
            moves_grid = self.grid

        availableSquares = []
        for nx, ny in self.findNeighboursDirect(x, y, moves_grid):
            if nx < 0 or ny < 0 or nx > moves_grid.shape[0] - 1 or ny > moves_grid.shape[1] - 1: continue
            xd = nx - x
            yd = ny - y
            if (nx == exclude_x and ny == exclude_y):
                continue
            if not check_carve:
                availableSquares.append((nx, ny))
            if self.canCarve(x, y, xd, yd):
                availableSquares.append((nx, ny))
        return availableSquares

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
                if self.grid[a+x, b+y]:
                    return False
        return True

    def floodFill(self, x, y, fillWith, tilesToFill = [], checked = None, unconnectedAreas = None, grid = None):
        #if not grid: grid = self.grid
        toFill = set()
        toFill.add((x,y))

        while toFill:
            x, y = toFill.pop()
            if tilesToFill and grid[x, y] not in tilesToFill: continue
            if not grid[x, y]: continue
            unconnectedAreas[x, y] = fillWith
            checked[x, y] = 1
            for nx, ny in self.findNeighboursDirect(x, y, grid):
                if unconnectedAreas[nx, ny] != fillWith:
                    toFill.add((nx, ny))

    def findUnconnectedAreas(self, tilesToFill = []):
        """
        Checks through the grid to find islands/unconnected rooms
        Note, this can be slow for large grids and memory intensive since it needs to create a deep copy of the grid
        in order to use joinUnconnectedAreas() this needs to be called first and the returned list passed to joinUnconnectedAreas()

        Args:
            none

        Returns:
            A list of unconnected cells, where each group of cells is in its own list and each cell indice is stored as a tuple, ie [[(x1,y1), (x2,y2), (x3,y3)], [(xi1,yi1), (xi2,yi2), (xi3,yi3)]]
        """
        areaCount = 0

        unconnectedAreas = np.zeros(self.grid.shape, dtype=np.int8)
        checked_cells = np.zeros(self.grid.shape, dtype=np.int8)

        choices = np.where(checked_cells == 0)

        gridCopy = self.grid.copy()

        gridCopy[0] = Tiles.EMPTY
        gridCopy[-1] = Tiles.EMPTY
        gridCopy[:, 0] = Tiles.EMPTY
        gridCopy[:, -1] = Tiles.EMPTY

        checked_cells[np.where(gridCopy == 0)] = 1

        while len(choices[0]) > 0:
            areaCount += 1
            self.floodFill(choices[0][0], choices[1][0], areaCount, tilesToFill = tilesToFill, checked = checked_cells, unconnectedAreas = unconnectedAreas, grid = gridCopy)

            choices = np.where(checked_cells == 0)

        return unconnectedAreas

    def joinUnconnectedAreas(self, unconnectedAreas, connecting_tile = Tiles.CORRIDOR_FLOOR):
        currentAreaCount = np.amax(unconnectedAreas)
        currentTiles = np.where(unconnectedAreas == currentAreaCount)

        while currentAreaCount > 1:
            nextAreaCount = currentAreaCount - 1
            nextTiles = np.where(unconnectedAreas == nextAreaCount)

            if len(nextTiles[0]) > 0:
                currentIdx = randint(0, len(currentTiles[0]) - 1)
                nextIdx = randint(0, len(nextTiles[0]) - 1)
                self.route_between(currentTiles[0][currentIdx], currentTiles[1][currentIdx], nextTiles[0][nextIdx], nextTiles[1][nextIdx], tile=connecting_tile)
                currentTiles = nextTiles

            currentAreaCount -= 1

    def turnAreasSmallerThanIntoWater(self, min_size = 20, tile = Tiles.SHALLOWWATER):
        unconnected = self.findUnconnectedAreas(tilesToFill = [Tiles.EMPTY])

        max = np.amax(unconnected)
        for i in range(max+1):
            area = np.where(unconnected == i)
            if (len(area[0]) < min_size):
                self.grid[area] = tile

    def removeAreasSmallerThan(self, min_size = 20, tile = Tiles.EMPTY):
        unconnected = self.findUnconnectedAreas()

        max = np.amax(unconnected)
        for i in range(max+1):
            area = np.where(unconnected == i)
            if (len(area[0]) < min_size):
                self.grid[area] = tile

    def generateCaves(self, probability = 45, smoothing = 4):
        cells = np.random.choice([0, 1], size=self.grid.shape, p=[probability/100, (100 - probability)/100])

        for i in range(smoothing):
            updated_cells = cells.copy()
            for (x,y), value in np.ndenumerate(cells):
                if self.grid[x, y] != Tiles.EMPTY:
                    updated_cells[x, y] = 0
                    continue

                touchingEmptySpace = np.sum(self.surrounding_tiles(x, y, cells))

                if touchingEmptySpace >= 6:
                    updated_cells[x, y] = 1
                elif touchingEmptySpace <= 3:
                    updated_cells[x, y] = 0

            cells = updated_cells;

        self.grid[np.where(cells == 1)] = Tiles.CAVERN_FLOOR

    def addRoom(self, x, y, width, height, margin = 1, overlap = False, add_door = False, add_walls = False, tile = Tiles.ROOM_FLOOR):
        room_slice = self.grid[x:x+width, y:y+height]

        final_room_slice = room_slice

        if room_slice.shape[0] != width or room_slice.shape[1] != height:
            print("Out of bounds")
            return None

        if not overlap and not self.quadFits(x, y, width, height, margin):
            return None

        if add_walls:
            outline_slice = self.grid[x-1:x+width+1, y-1:y+height+1]
            if outline_slice.shape[0] != (width + 2) or outline_slice.shape[1] != (height + 2):
                print("Bad shape: " + str(outline_slice.shape))
                return None
            outline_slice[np.where(outline_slice != Tiles.IMPENETRABLE)] = floor_to_wall[tile]

            final_room_slice = outline_slice

        room_slice[:] = tile

        if add_door:
            outline_slice = self.grid[x-1:x+width+1, y-1:y+height+1]

            a,b = np.ogrid[x-1:x+width+1, y-1:y+height+1]
            #This gets the outline of the room EXCLUDING the corners
            door_mask = ((a >= x) & (a < x+width)) | ((b >= y) & (b < y+height))
            #This gets ths floor of the room
            door_mask2 = (a >= x) & (a < x+width) & (b >= y) & (b < y+height)
            #Exclude impenetrable tiles (e.g. the edges)
            impenetrable_mask = outline_slice != Tiles.IMPENETRABLE

            #We combine the above so we get a mask of possible door positions on
            #the outside of the room
            final_door_mask = (door_mask == True) & (door_mask2 == False) & (impenetrable_mask == True)

            possible_door_place = np.where(final_door_mask == True)

            max_doors = 2
            num_doors = randint(1, max_doors)
            for door in range(num_doors):
                if len(possible_door_place[0]) > 1:
                    idx = randint(1, len(possible_door_place[0]) - 1)
                    outline_slice[possible_door_place[0][idx], possible_door_place[1][idx]] = Tiles.DOOR

            final_room_slice = outline_slice

        room = dungeonRoom(x, y, final_room_slice.copy)

        return room

    def addCircleShapedRoom(self, x, y, radius = 5, margin = 1, overlap = False, add_door = True, add_walls = False, tile = Tiles.ROOM_FLOOR):
        width = (2*radius)+1
        room_slice = self.grid[x:x+width, y:y+width]

        final_room_slice = room_slice

        if room_slice.shape[0] != width or room_slice.shape[1] != width:
            print("Out of bounds")
            return None

        if not overlap and not self.quadFits(x, y, room_slice.shape[0], room_slice.shape[1], margin):
            return None

        if add_walls:
            y1,x1 = np.ogrid[-radius-1:radius+1, -radius-1:radius+1]
            mask = x1**2 + y1**2 < (radius+1)**2
            wall_slice = self.grid[x-1:x+width, y-1:y+width]
            wall_slice[mask] = floor_to_wall[tile]

        y1,x1 = np.ogrid[-radius:radius+1, -radius:radius+1]
        mask2 = x1**2 + y1**2 < (radius)**2
        room_slice[mask2] = tile

        donut = choice([True, False])

        if donut and (radius > 4):
            donut_radius = randint((radius // 2) + 1, radius - 2)

            y1,x1 = np.ogrid[-radius:radius+1, -radius:radius+1]
            mask3 = x1**2 + y1**2 < (donut_radius)**2
            room_slice[mask3] = choice([Tiles.SHALLOWWATER, Tiles.EMPTY])

        if add_door:
            max_doors = 4
            num_doors = randint(1, max_doors)
            possible_door_place = [(1, radius+1), (radius+1, width), (radius+1, 1), (width, radius+1)]
            outline_slice = self.grid[x-1:x+width, y-1:y+width]

            for door in range(num_doors):
                if len(possible_door_place):
                    idx = randint(0, len(possible_door_place)-1)
                    x, y = possible_door_place[idx]
                    outline_slice[x, y] = Tiles.DOOR
                    del possible_door_place[idx]
            final_room_slice = outline_slice

        room = dungeonRoom(x, y, final_room_slice.copy)

        return room

    def placeRoomRandomly(self, prefab, margin = 1, attempts = 500):
        for attempt in range(attempts):
            start_x, start_y = self.randomPoint(tile=Tiles.EMPTY, x_inset = prefab.layout.shape[0] + (margin * 2), y_inset = prefab.layout.shape[1] + (margin * 2))

            if self.quadFits(start_x, start_y, prefab.layout.shape[0], prefab.layout.shape[1], margin):
                try:
                    self.grid[start_x:start_x+prefab.layout.shape[0], start_y:start_y+prefab.layout.shape[1]] = prefab.layout
                except ValueError:
                    print(f"placeRoomRandomly failed: {start_x},{start_y} {prefab.shape}")
                    return None

                room = dungeonRoom(x, y, prefab.layout.copy)

                return room

        return None

    def placeRandomRooms(self, minRoomSize, maxRoomSize, roomStep = 1, margin = 3, attempts = 500, add_door = False, add_walls = False):
        for attempt in range(attempts):
            roomWidth = randrange(minRoomSize, maxRoomSize, roomStep)
            roomHeight = randrange(minRoomSize, maxRoomSize, roomStep)
            startX = randint(1, self.grid.shape[0] - roomWidth)
            startY = randint(1, self.grid.shape[1] - roomHeight)

            if roomWidth == roomHeight:
                room = self.addCircleShapedRoom(startX, startY, roomWidth, margin = margin, add_door = add_door, add_walls = add_walls)
            else:
                room = self.addRoom(startX, startY, roomWidth, roomHeight, margin = margin, add_door = add_door, add_walls = add_walls)

            if room:
                self.rooms.append(room)

    def connectDoors(self):
        doors = np.where(self.grid == Tiles.DOOR)

        door_tuples = tuple(zip(doors[0],doors[1]))

        weights = [(Tiles.CORRIDOR_FLOOR, 2),
                    (Tiles.EMPTY, 9),
                    (Tiles.CAVERN_FLOOR, 2),
                    (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1)]

        for x1, y1 in door_tuples:
            num_connections = randint(1, len(doors[0]))
            for i in range(num_connections):
                idx = randint(0, len(doors[0]) - 1)
                self.route_between(x1, y1, doors[0][idx], doors[1][idx], avoid = [Tiles.ROOM_FLOOR, Tiles.ROOM_WALL], weights = weights, overwrite = True)

    def cleanUpMap(self):
        self.grid[np.where(self.grid == Tiles.POTENTIAL_CORRIDOR_FLOOR)] = Tiles.EMPTY

        self.grid[0] = Tiles.EMPTY
        self.grid[-1] = Tiles.EMPTY
        self.grid[:, 0] = Tiles.EMPTY
        self.grid[:, -1] = Tiles.EMPTY

        self.deepWater()

        self.placeWalls()

    def placeWalls(self):
        tiles = np.where(self.grid != 0)
        tiles_tuples = tuple(zip(tiles[0],tiles[1]))

        for x, y in tiles_tuples:
            if self.grid[x, y] in WALKABLE_TILES:
                surrounding = self.surrounding_tiles(x,y)
                surrounding[np.where(surrounding == Tiles.EMPTY)] = floor_to_wall[self.grid[x,y]]

    def route_between(self, x1, y1, x2, y2, tile=Tiles.CORRIDOR_FLOOR, avoid = [], weights = [], overwrite = False):

        dijk, dijk_dist = self.create_dijkstra_map(x1, y1, default_weight = 1, avoid = avoid, weights = weights)

        tcod.dijkstra_path_set(dijk, x2, y2)

        for i in range(tcod.dijkstra_size(dijk)):
            x, y = tcod.dijkstra_get(dijk, i)
            if overwrite or self.grid[x,y] == 0:
                if self.grid[x,y] == Tiles.DOOR:
                    continue
                self.grid[x,y] = tile

        return dijk_dist

    def create_dijkstra_map(self, x1, y1, default_weight = 1, avoid = [], weights = []):
        walkable = np.zeros(self.grid.shape, dtype=np.int8)
        walkable[np.where(self.grid != Tiles.EMPTY)] = default_weight

        avoid.append(Tiles.IMPENETRABLE)
        mask = np.isin(self.grid, avoid)

        walkable[mask] = 0

        for tile, weight in weights:
            walkable[np.where(self.grid == tile)] = weight

        dijk = tcod.dijkstra_new(walkable, 0)
        tcod.dijkstra_compute(dijk, x1, y1)

        dijk_dist = np.zeros(walkable.shape, dtype=np.int8)
        for (x,y), value in np.ndenumerate(dijk_dist):
            dijk_dist[x, y] = tcod.dijkstra_get_distance(dijk, x, y)

        dijk_dist[np.where(dijk_dist == -1)] = 0

        return dijk, dijk_dist

    def generateCorridors(self, mode = 'r', x = None, y = None):
        """
        Generates a maze of corridors on the growing tree algorithm,
        where corridors do not overlap with over tiles, are 1 tile away from anything else and there are no diagonals

        Args:
            mode: char, either 'r', 'f', 'm' or 'l'
                  This controls how the next tile to attempt to move to is determined and affects how the generated corridors look
                  'r' - random selection, produces short straight sections with spine like off-shoots, lots of deadends
                  'f' - first cell in the list to check, long straight secions and few diagonal snaking sections
                  'm' - similar to first but more likely to snake
                  'l' - snaking and winding corridor sections
            x and y: integer, grid indicies, starting point for the corridor generation,
                     if none is provided a random one will be chosen

            Returns:
                none
        """

        cells = []
        if not x and not y:
            x, y = self.randomPoint()

        self.grid[x, y] = Tiles.POTENTIAL_CORRIDOR_FLOOR

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
            #print(f"corridor: {x}, {y}")
            possMoves = self.getPossibleMoves(x, y)
            #print(possMoves)
            if possMoves:
                xi, yi = choice(possMoves)
                self.grid[xi, yi] = Tiles.POTENTIAL_CORRIDOR_FLOOR
                cells.append((xi, yi))
            else:
                cells.remove((x, y))

    def boundedDrunkenWalk(self, source_x, source_y, target_x, target_y, previous_x = None, previous_y = None, total = 0, tile = Tiles.CAVERN_FLOOR, walk_grid = None, overwrite = False):
        if source_x == target_x and source_y == target_y:
            print("Joy!")
            return True

        if total > 500:
            print("Too many attempts")
            return False

        if walk_grid is None:
            start_x = min(source_x, target_x)
            end_x = max(source_x, target_x)
            start_y = min(source_y, target_y)
            end_y = max(source_y, target_y)

            walk_grid = self.grid[start_x:end_x+1, start_y:end_y+1]
            walk_grid[:] = Tiles.DEEPWATER

            source_x -= start_x
            source_y -= start_y

            target_x -= start_x
            target_y -= start_y

        if overwrite or (self.grid[source_x, source_y] == Tiles.EMPTY or self.grid[source_x, source_y] in BLOCKING_TILES):
            walk_grid[source_x, source_y] = tile

        moves = self.getPossibleMoves(source_x, source_y, previous_x, previous_y, walk_grid)

        if (len(moves) < 1):
            print("out of moves")
            return False

        previous_x = source_x
        previous_y = source_y

        distances = []
        for x, y in moves:
            distance = self.distanceBetween(x, y, target_x, target_y)
            #if distance == 1:
            #    print("Within 1 space", total)
            #    return True
            distances.append((distance, (x,y)))

        distances.sort(key = operator.itemgetter(0))

        idx = 0
        if (len(distances) > 1):
            idx = randint(0,1)

        source_x, source_y = distances[idx][1]

        if source_x == target_x and source_y == target_y:
            print("Joy!")
            return True

        total += 1
        return self.boundedDrunkenWalk(source_x, source_y, target_x, target_y, previous_x, previous_y, total, tile, walk_grid, overwrite)

    def drunkenWalk(self, source_x, source_y, target_x, target_y, previous_x = None, previous_y = None, total = 0, tile = Tiles.CAVERN_FLOOR, overwrite = False):
        if source_x == target_x and source_y == target_y:
            return True

        if total > 500:
            print("Too many attempts")
            return False

        if overwrite or (self.grid[source_x, source_y] == Tiles.EMPTY or self.grid[source_x, source_y] in BLOCKING_TILES):
            self.grid[source_x, source_y] = tile

        moves = self.getPossibleMoves(source_x, source_y, previous_x, previous_y, check_carve = False)

        if (len(moves) < 1):
            print("out of moves")
            return False

        previous_x = source_x
        previous_y = source_y

        distances = []
        for x, y in moves:
            distance = self.distanceBetween(x, y, target_x, target_y)
            distances.append((distance, (x,y)))

        distances.sort(key = operator.itemgetter(0))

        idx = 0
        if (len(distances) > 1):
            idx = randint(0,1)

        source_x, source_y = distances[idx][1]

        total += 1
        return self.drunkenWalk(source_x, source_y, target_x, target_y, previous_x, previous_y, total, tile, overwrite  )

    def surrounding_tiles(self, x, y, grid = None):
        if grid is None:
            grid = self.grid

        offset_x = -1

        offset_y = -1

        tiles_slice = grid[x-1:x+2, y-1:y+2]

        return tiles_slice

    def distanceBetween(self, x1, y1, x2, y2):
        #return the distance to another point
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return sqrt(dx ** 2 + dy ** 2)

    def findEmptySpace(self, inset = 1, attempts = 3):

        count = 0
        while count < attempts:
            x, y = self.randomPoint(x_inset = inset, y_inset = inset)

            if x and y:
                max = np.amax(self.grid[x-1:x+2, y-1:y+2])

                if max == 0:
                    print('found a blank space!')
                    return x, y
            count += 1

        return None, None

    def randomPoint(self, tile=Tiles.EMPTY, x_inset = 0, y_inset = 0):
        search_grid = self.grid[x_inset:self.grid.shape[0]-x_inset, y_inset:self.grid.shape[1]-y_inset]

        tiles = np.where(search_grid == tile)

        if len(tiles[0]) < 1:
            return None, None

        idx = randint(0, len(tiles[0]) - 1)

        return tiles[0][idx] + x_inset, tiles[1][idx] + y_inset

    def waterFeature(self):
        x1, y1 = self.randomPoint(tile=Tiles.EMPTY)
        x2, y2 = self.randomPoint(tile=Tiles.EMPTY)

        self.drunkenWalk(x1,y1,x2,y2,tile=Tiles.SHALLOWWATER, overwrite = True)

    def deepWater(self):
        tiles = np.where(self.grid == Tiles.SHALLOWWATER)

        water_grid = self.grid.copy()
        for idx, x in enumerate(tiles[0]):
            y = tiles[1][idx]

            surronding = self.surrounding_tiles(x,y)
            surrounding_water = np.where(surronding == Tiles.SHALLOWWATER)

            if len(surrounding_water[0]) == 9:
                water_grid[x,y] = Tiles.DEEPWATER

        self.grid[:] = water_grid[:]

    def validateMap(self):
        stairs = np.where(self.grid == Tiles.STAIRSFLOOR)

        if len(stairs[0]) < 2:
            print("Not enough exits")
            return False

        walkable = self.grid.copy()
        mask = np.isin(self.grid, [Tiles.OBSTACLE, Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL, Tiles.DEEPWATER, Tiles.IMPENETRABLE])
        walkable[mask] = 0

        astar = tcod.path.AStar(walkable, 0)
        path = astar.get_path(stairs[0][0], stairs[1][0], stairs[0][1], stairs[1][1])

        if len(path) < 1:
            print("Can't route between stairs")
            return False

        return True
