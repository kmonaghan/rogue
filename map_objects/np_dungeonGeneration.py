import logging
from math import sqrt
import numpy as np
import operator
from random import choice, randint, randrange, shuffle

import tcod

#tile constants
from etc.enum import Tiles, WALKABLE_TILES, BLOCKING_TILES
from etc.exceptions import RoomOutOfBoundsError, RoomOverlapsError

floor_to_wall = {
    Tiles.OBSTACLE: Tiles.CAVERN_WALL,
    Tiles.IMPENETRABLE: Tiles.IMPENETRABLE,
    Tiles.CAVERN_FLOOR: Tiles.CAVERN_WALL,
    Tiles.FUNGAL_CAVERN_FLOOR: Tiles.CAVERN_WALL,
    Tiles.DEADEND: Tiles.CORRIDOR_WALL,
    Tiles.CORRIDOR_FLOOR: Tiles.CORRIDOR_WALL,
    Tiles.ROOM_FLOOR: Tiles.ROOM_WALL,
    Tiles.ROOM_WALL: Tiles.ROOM_WALL,
    Tiles.STAIRS_FLOOR: Tiles.ROOM_WALL,
    Tiles.DEEP_WATER: Tiles.CAVERN_WALL,
    Tiles.SHALLOW_WATER: Tiles.CAVERN_WALL,
    Tiles.DOOR: Tiles.ROOM_WALL,
}

wall_to_floor = {
    Tiles.CAVERN_WALL: Tiles.CAVERN_FLOOR,
    Tiles.CORRIDOR_WALL: Tiles.CORRIDOR_FLOOR,
    Tiles.ROOM_WALL: Tiles.DOOR,
}

from utils.utils import matprint

def surrounding_tiles(x, y, grid):
    tiles_slice = grid[x-1:x+2, y-1:y+2]

    return tiles_slice

#See http://www.darkgnosis.com/2018/03/03/contour-bombing-cave-generation-algorithm
def random_walk(shape, reset=False, percentage=60):
    cells = np.zeros(shape, dtype=np.int8)

    current_x = start_x = randint(0,shape[0] - 1)
    current_y = start_y = randint(0,shape[1] - 1)

    path_length = ((shape[0] * shape[1]) * percentage) // 100
    steps = 0

    for i in range(path_length):
        next = randint(0,3)
        if next == 0:
            #Move to the left
            dx = -1
            dy = 0
        elif next == 1:
            #Move to the right
            dx = 1
            dy = 0
        elif next == 2:
            #Move to up
            dx = 0
            dy = -1
        elif next == 3:
            #Move down
            dx = 0
            dy = 1

        current_x = max(0, min(shape[0] - 1, current_x + dx))
        current_y = max(0, min(shape[1] - 1, current_y + dy))

        cells[current_x, current_y] = 1

        steps = steps + 1

        if reset and steps >= 100:
            steps = 0
            current_x = start_x
            current_y = start_y

    return cells

def cellular_map(shape, probability = 45, smoothing = 4):
    cells = np.random.choice([0, 1], size=shape, p=[probability/100, (100 - probability)/100])

    for i in range(smoothing):
        updated_cells = cells.copy()
        for (x,y), value in np.ndenumerate(cells):
            touchingEmptySpace = np.sum(surrounding_tiles(x, y, cells))

            if touchingEmptySpace >= 6:
                updated_cells[x, y] = 1
            elif touchingEmptySpace <= 3:
                updated_cells[x, y] = 0

        cells = updated_cells;

    #Don't touch the edge
    cells[0] = 0
    cells[-1] = 0
    cells[:, 0] = 0
    cells[:, -1] = 0

    return cells

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

    def __init__(self, x, y, slice, name=""):
        self.x = x
        self.y = y
        self.layout = slice.copy()
        self.name = name

    def __str__(self):
        return f"{self.name} {self.x},{self.y} {self.layout.shape}"

    def __repr__(self):
        return f"{self.name} {self.x},{self.y} {self.layout.shape}"

    @property
    def width(self):
        return self.layout.shape[0]

    @property
    def height(self):
        return self.layout.shape[1]

    @property
    def center(self):
        return (self.x + (self.width // 2), self.y + (self.height // 2))

class prefabRoom(dungeonRoom):
    def __init__(self, x, y, slice, name="", exits=[], spawnpoints=[]):
        super(prefabRoom, self).__init__(x, y, slice, name)
        self.mask = np.full(self.layout.shape, 1, dtype=np.int8)

        empty_tiles = np.isin(self.layout, [Tiles.EMPTY])

        self.mask[empty_tiles] = 0
        self.exits = exits
        for x,y in self.exits:
            self.mask[x,y] = 0
        self.spawnpoints = spawnpoints

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
        return self.grid.shape[1]

    def quadFits(self, sx, sy, rx, ry, margin):
        top_x = max(0, sx-margin)
        top_y = max(0, sy-margin)

        bottom_x = min(self.grid.shape[0] - 1, sx+rx+margin)
        bottom_y = min(self.grid.shape[1] - 1, sy+ry+margin)

        room_bounds = self.grid[top_x:bottom_x, top_y:bottom_y]

        if np.count_nonzero(room_bounds) > 0:
            #logging.info("Another feature is too close.")
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

    def emptyFloodFill(self, x, y, fillWith, checked = None, unconnectedAreas = None, grid = None):
        #if not grid: grid = self.grid
        toFill = set()
        toFill.add((x,y))

        while toFill:
            x, y = toFill.pop()
            if grid[x, y] == Tiles.EMPTY:
                unconnectedAreas[x, y] = fillWith
                checked[x, y] = 1
                for nx, ny in self.findNeighboursDirect(x, y, grid):
                    if unconnectedAreas[nx, ny] != fillWith:
                        toFill.add((nx, ny))

    def findEmptyAreas(self, tilesToFill = []):
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

        gridCopy = self.grid.copy()

        gridCopy[0] = Tiles.EMPTY
        gridCopy[-1] = Tiles.EMPTY
        gridCopy[:, 0] = Tiles.EMPTY
        gridCopy[:, -1] = Tiles.EMPTY

        checked_cells[np.where(gridCopy > 0)] = 1
        choices = np.where(checked_cells == 0)

        while len(choices[0]) > 0:
            areaCount += 1
            self.emptyFloodFill(choices[0][0], choices[1][0], areaCount, checked = checked_cells, unconnectedAreas = unconnectedAreas, grid = gridCopy)

            choices = np.where(checked_cells == 0)

        return unconnectedAreas

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

        gridCopy = self.grid.copy()

        gridCopy[0] = Tiles.EMPTY
        gridCopy[-1] = Tiles.EMPTY
        gridCopy[:, 0] = Tiles.EMPTY
        gridCopy[:, -1] = Tiles.EMPTY

        checked_cells[np.where(gridCopy == 0)] = 1
        choices = np.where(checked_cells == 0)

        while len(choices[0]) > 0:
            areaCount += 1
            self.floodFill(choices[0][0], choices[1][0], areaCount, tilesToFill = tilesToFill, checked = checked_cells, unconnectedAreas = unconnectedAreas, grid = gridCopy)

            choices = np.where(checked_cells == 0)

        return unconnectedAreas

    def joinUnconnectedAreas(self, unconnectedAreas, connecting_tile = Tiles.CORRIDOR_FLOOR):
        currentAreaCount = np.amax(unconnectedAreas)
        currentTiles = np.where(unconnectedAreas == currentAreaCount)

        weights = [(Tiles.EMPTY, 9),
                    (Tiles.ROOM_WALL, 9)]

        while currentAreaCount > 1:
            nextAreaCount = currentAreaCount - 1
            nextTiles = np.where(unconnectedAreas == nextAreaCount)

            if len(nextTiles[0]) > 0:
                currentIdx = randint(0, len(currentTiles[0]) - 1)
                nextIdx = randint(0, len(nextTiles[0]) - 1)
                self.route_between(currentTiles[0][currentIdx], currentTiles[1][currentIdx],
                                    nextTiles[0][nextIdx], nextTiles[1][nextIdx],
                                    weights=weights, tile=connecting_tile)
                currentTiles = nextTiles

            currentAreaCount -= 1

    def turnAreasSmallerThanIntoWater(self, min_size = 20, tile = Tiles.SHALLOW_WATER):
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
        cells = cellular_map(self.grid.shape, probability, smoothing)

        self.grid[np.where(cells == 1)] = Tiles.CAVERN_FLOOR

    def addRoom(self, x, y, width, height, margin = 1, overlap = False, add_door = False, add_walls = False, tile = Tiles.ROOM_FLOOR, name = "", max_doors=4):
        offset = 0
        if add_walls:
            offset = 2

        room_slice = self.grid[x:x+width+offset, y:y+height+offset]

        if room_slice.shape[0] != (width + offset) or room_slice.shape[1] != (height + offset):
            #logging.info("Room position out of bounds")
            raise RoomOutOfBoundsError

        if not overlap and not self.quadFits(x, y, room_slice.shape[0], room_slice.shape[1], margin):
            #logging.info("Failed due to overlap/quadfits")
            raise RoomOverlapsError

        room_slice[:] = tile

        if add_walls:
            room_slice[0] = floor_to_wall[tile]
            room_slice[-1] = floor_to_wall[tile]
            room_slice[:, 0] = floor_to_wall[tile]
            room_slice[:, -1] = floor_to_wall[tile]

            if add_door:
                self.addDoorsToRoom(x, y, width, height, room_slice, tile, max_doors)

        room = dungeonRoom(x, y, room_slice, name)

        self.rooms.append(room)

        return room

    def addDoorsToRoom(self, x, y, width, height, room_slice, tile, max_doors=4):
        a,b = np.ogrid[x:x+width+2, y:y+height+2]
        #This gets the outline of the room EXCLUDING the corners
        door_mask = ((a > x) & (a < x+width+1)) | ((b > y) & (b < y+height+1))
        #There needs to 2 spaces between the wall and the edge of the map.
        #If there isn't, mask it out.
        #logging.info(f"{x} <= 1")
        if (x <= 1):
            door_mask[0] = False
        #logging.info(f"{x+width+3} >= {self.grid.shape[0]}")
        if (x+width+3 >= self.grid.shape[0]):
            door_mask[-1] = False
        #logging.info(f"{y} <= 1")
        if (y <= 1):
            door_mask[:, 0] = False
        #logging.info(f"{y+height+3} >= {self.grid.shape[1]}")
        if (y+height+3 >= self.grid.shape[1]):
            door_mask[:, -1] = False

        #This gets ths floor of the room
        floor_mask = room_slice == tile

        #This gets ths floor of the room
        empty_mask = room_slice == Tiles.EMPTY

        #Exclude impenetrable tiles (e.g. the edges)
        impenetrable_mask = room_slice != Tiles.IMPENETRABLE

        #We combine the above so we get a mask of possible door positions on
        #the outside of the room
        final_door_mask = (door_mask == True) & (floor_mask == False) & (empty_mask == False) & (impenetrable_mask == True)

        possible_door_place = np.where(final_door_mask == True)

        num_doors = randint(1, max_doors)
        for door in range(num_doors):
            if len(possible_door_place[0]) > 1:
                idx = randint(1, len(possible_door_place[0]) - 1)
                room_slice[possible_door_place[0][idx], possible_door_place[1][idx]] = Tiles.DOOR

# Uses Numpy to carve a circle into the map
# See: https://stackoverflow.com/questions/8647024/how-to-apply-a-disc-shaped-mask-to-a-numpy-array
    def addCircleShapedRoom(self, x, y, radius = 5, margin = 1, overlap = False, add_door = True, add_walls = False, tile = Tiles.ROOM_FLOOR, max_doors = 4):

        if add_walls:
            radius = radius + 1
        full_radius = radius

        width = (2*radius)+1
        room_slice = self.grid[x:x+width, y:y+width]

        if room_slice.shape[0] < width or room_slice.shape[1] < width:
            #logging.info("Circle room out of bounds")
            return None

        if not overlap and not self.quadFits(x, y, room_slice.shape[0], room_slice.shape[1], margin):
            #logging.info("Circle room failed quad fit")
            return None

        if add_walls:
            y1,x1 = np.ogrid[-full_radius:full_radius+1, -full_radius:full_radius+1]
            mask2 = x1**2 + y1**2 <= (radius+1)**2
            room_slice[mask2] = floor_to_wall[tile]

            if add_door:
                num_doors = randint(1, max_doors)

                possible_door_place = []
                if x >=2:
                    possible_door_place.append((0, radius))
                if y >=2:
                    possible_door_place.append((radius, 0))
                if x <= self.grid.shape[0] - width - 2:
                    possible_door_place.append((width-1, radius))
                if y <= self.grid.shape[1] - width - 2:
                    possible_door_place.append((radius, width-1))

                #logging.info(f"Doors: {num_doors} from: {possible_door_place}")
                for door in range(num_doors):
                    if len(possible_door_place):
                        idx = randint(0, len(possible_door_place)-1)
                        door_x, door_y = possible_door_place[idx]
                        room_slice[door_x, door_y] = Tiles.DOOR
                        del possible_door_place[idx]
            radius = radius - 1

        y1,x1 = np.ogrid[-full_radius:full_radius+1, -full_radius:full_radius+1]
        mask2 = x1**2 + y1**2 < (radius+1)**2
        room_slice[mask2] = tile

        donut = choice([True, False])
        if donut and (radius > 4):
            donut_radius = randint((full_radius // 2) + 1, full_radius - 2)

            y1,x1 = np.ogrid[-full_radius:full_radius+1, -full_radius:full_radius+1]
            mask3 = x1**2 + y1**2 < (donut_radius)**2
            interior_tile = choice([Tiles.SHALLOW_WATER, Tiles.EMPTY])
            room_slice[mask3] = interior_tile

            if (interior_tile == Tiles.EMPTY):
                y1,x1 = np.ogrid[-full_radius:full_radius+1, -full_radius:full_radius+1]
                mask3 = x1**2 + y1**2 < (donut_radius)**2
                room_slice[mask3] = floor_to_wall[tile]

                if (donut_radius > 5):
                    y1,x1 = np.ogrid[-full_radius:full_radius+1, -full_radius:full_radius+1]
                    mask4 = x1**2 + y1**2 < (donut_radius-1)**2
                    room_slice[mask4] = Tiles.EMPTY

        room = dungeonRoom(x, y, room_slice)

        self.rooms.append(room)

        return room

    def placeRoomRandomly(self, prefab, margin = 1, attempts = 500, overwrite = True):
        for attempt in range(attempts):
            start_x, start_y = self.randomPoint(tile=Tiles.EMPTY, x_inset = prefab.layout.shape[0] + (margin * 2), y_inset = prefab.layout.shape[1] + (margin * 2))

            if not start_x:
                #logging.info("Failed to place room as ran out of empty tiles")
                return None

            if overwrite or self.quadFits(start_x, start_y, prefab.layout.shape[0], prefab.layout.shape[1], margin):
                try:
                    self.grid[start_x:start_x+prefab.layout.shape[0], start_y:start_y+prefab.layout.shape[1]] = prefab.layout
                except ValueError:
                    #logging.info(f"placeRoomRandomly failed: {start_x},{start_y} {prefab.shape}")
                    return None

                room = prefabRoom(start_x, start_y, prefab.layout, prefab.name, prefab.exits, prefab.spawnpoints)

                self.rooms.append(room)

                return room

        return None

    def placeLargeRoom(self, width=15, height=15):
        template = np.full((5,5), Tiles.ROOM_FLOOR, dtype=np.int8)

        template[0] = Tiles.ROOM_WALL
        template[-1] = Tiles.ROOM_WALL
        template[:, 0] = Tiles.ROOM_WALL
        template[:, -1] = Tiles.ROOM_WALL

        template[0,-1] = Tiles.DEEP_WATER
        template[0,0] = Tiles.DEEP_WATER
        template[-1,0] = Tiles.DEEP_WATER
        template[-1,-1] = Tiles.DEEP_WATER

        room = np.zeros((width, height), dtype=np.int8)

        x = randint(0,width-template.shape[0])
        y = randint(0,height-template.shape[1])

        room_slice = room[x:x+template.shape[0], y:y+template.shape[1]]

        room_slice[np.where(room_slice == Tiles.EMPTY)] = template[np.where(room_slice == Tiles.EMPTY)]

        for i in range(9):
            floor = np.where(room == Tiles.ROOM_FLOOR)

            if len(floor[0]) < 1:
                logging.info("Out of space to place room")
                return

            pick = randint(0,len(floor[0]) - 1)
            x = floor[0][pick]
            y = floor[1][pick]

            room_slice = room[x:x+template.shape[0], y:y+template.shape[1]]

            room_slice[np.where(room_slice == Tiles.EMPTY)] = template[np.where(room_slice == Tiles.EMPTY)]

            room_slice[np.where((room_slice == Tiles.ROOM_WALL) & (template == Tiles.ROOM_WALL))] = Tiles.DEEP_WATER

            room_slice[1:template.shape[0]-1, 1:template.shape[1]-1] = Tiles.ROOM_FLOOR

            logging.info(f"Added detail at {x} {y}")
            matprint(room)

    def placeRandomRooms(self, minRoomSize, maxRoomSize, roomStep = 1, margin = 3,
                            attempts = 500, add_door = False, add_walls = False,
                            overlap = False):
        for attempt in range(attempts):
            roomWidth = randrange(minRoomSize, maxRoomSize, roomStep)
            roomHeight = randrange(minRoomSize, maxRoomSize, roomStep)

            voids = np.where(self.grid == Tiles.EMPTY)

            if len(voids[0]) < 1:
                logging.info("Out of space to place room")
                return

            pick = randint(0,len(voids[0]) - 1)
            startX = voids[0][pick]
            startY = voids[1][pick]

            room = None

            try:
                if (roomWidth == roomHeight) and (roomWidth > 5):
                    room = self.addCircleShapedRoom(startX, startY, roomWidth // 2, overlap = overlap, margin = margin, add_door = add_door, add_walls = add_walls)
                else:
                    room = self.addRoom(startX, startY, roomWidth, roomHeight, overlap = overlap, margin = margin, add_door = add_door, add_walls = add_walls)
            except (RoomOverlapsError, RoomOutOfBoundsError) as e:
                pass

            if room:
                self.rooms.append(room)

    def connectRooms(self):
        room_list = self.rooms.copy()

        shuffle(room_list)

        while len(room_list) >= 2:
            current_room = room_list.pop(0)

            self.connectDoorsToRooms(current_room, room_list)

        final_room_list = self.rooms.copy()
        final_room_list.remove(room_list[0])

        self.connectDoorsToRooms(room_list[0], final_room_list)

    def connectDoorsToRooms(self, room, room_list):
        weights = [(Tiles.CORRIDOR_FLOOR, 2),
                    (Tiles.EMPTY, 8),
                    (Tiles.CAVERN_FLOOR, 2),
                    (Tiles.POTENTIAL_CORRIDOR_FLOOR, 1),
                    (Tiles.DOOR, 9)]

        doors = np.where(room.layout == Tiles.DOOR)

        current_door_tuples = tuple(zip(doors[0],doors[1]))

        if len(current_door_tuples) == 0:
            #logging.info(f"No doors in {room}")
            return

        idx = 0
        for x1, y1 in current_door_tuples:
            x1 = x1 + room.x
            y1 = y1 + room.y

            target_room = room_list[idx]

            target_doors = np.where(target_room.layout == Tiles.DOOR)
            target_door_tuples = tuple(zip(target_doors[0],target_doors[1]))

            target_idx = randint(0, len(target_doors[0]) - 1)

            self.route_between(x1, y1, target_doors[0][target_idx] + target_room.x, target_doors[1][target_idx] + target_room.y, avoid = [Tiles.ROOM_FLOOR, Tiles.ROOM_WALL], weights = weights)

            idx = randint(0, len(room_list) - 1)

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
                self.route_between(x1, y1, doors[0][idx], doors[1][idx], avoid = [Tiles.ROOM_FLOOR, Tiles.ROOM_WALL], weights = weights)

    def cleanUpMap(self):
        self.grid[np.where(self.grid == Tiles.POTENTIAL_CORRIDOR_FLOOR)] = Tiles.EMPTY

        self.grid[np.where(self.grid == Tiles.IMPENETRABLE)] = Tiles.EMPTY

        self.DeepWater()

        self.placeWalls()

    def placeWalls(self):
        tiles = np.where(self.grid != 0)
        tiles_tuples = tuple(zip(tiles[0],tiles[1]))

        for x, y in tiles_tuples:
            if self.grid[x, y] in WALKABLE_TILES:
                surrounding = surrounding_tiles(x,y,self.grid)
                surrounding[np.where(surrounding == Tiles.EMPTY)] = floor_to_wall[self.grid[x,y]]

    def route_between(self, x1, y1, x2, y2, tile=Tiles.CORRIDOR_FLOOR, avoid = [], weights = [], overwrite = False, avoid_rooms = False):

        dijk, dijk_dist = self.create_dijkstra_map(x1, y1, default_weight = 1, avoid = avoid, weights = weights, avoid_rooms = avoid_rooms)

        tcod.dijkstra_path_set(dijk, x2, y2)

        for i in range(tcod.dijkstra_size(dijk)):
            x, y = tcod.dijkstra_get(dijk, i)
            if overwrite:
                self.grid[x,y] = tile
            else:
                replacement_tile = self.grid[x,y]
                if self.grid[x,y] in BLOCKING_TILES:
                    replacement_tile = self.grid[x,y] = wall_to_floor.get(self.grid[x,y], tile)
                elif self.grid[x,y] == Tiles.EMPTY:
                    replacement_tile = tile
                elif self.grid[x,y] == Tiles.POTENTIAL_CORRIDOR_FLOOR:
                    replacement_tile = Tiles.CORRIDOR_FLOOR
                self.grid[x,y] = replacement_tile

        return dijk_dist

    def create_dijkstra_map(self, x1, y1, default_weight = 1, avoid = [], weights = [], avoid_rooms = False):
        walkable = np.zeros(self.grid.shape, dtype=np.int8)
        walkable[np.where(self.grid != Tiles.EMPTY)] = default_weight

        avoid.append(Tiles.IMPENETRABLE)
        mask = np.isin(self.grid, avoid)

        walkable[mask] = 0

        for tile, weight in weights:
            walkable[np.where(self.grid == tile)] = weight

        if avoid_rooms:
            for room in self.rooms:
                if isinstance(room, prefabRoom):
                    room_slice = walkable[room.x:room.x+room.width, room.y:room.y+room.height]
                    room_slice[np.where(room.mask == 1)] = 0

        dijk = tcod.dijkstra_new(walkable, 0)
        tcod.dijkstra_compute(dijk, x1, y1)

        dijk_dist = np.zeros(walkable.shape, dtype=np.int8)
        for (x,y), value in np.ndenumerate(dijk_dist):
            dijk_dist[x, y] = tcod.dijkstra_get_distance(dijk, x, y)

        #dijk_dist[np.where(dijk_dist == -1)] = 0

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
            #logging.info(f"corridor: {x}, {y}")
            possMoves = self.getPossibleMoves(x, y)
            #logging.info(possMoves)
            if possMoves:
                xi, yi = choice(possMoves)
                self.grid[xi, yi] = Tiles.POTENTIAL_CORRIDOR_FLOOR
                cells.append((xi, yi))
            else:
                cells.remove((x, y))

    def boundedDrunkenWalk(self, source_x, source_y, target_x, target_y, previous_x = None, previous_y = None, total = 0, tile = Tiles.CAVERN_FLOOR, walk_grid = None, overwrite = False):
        if source_x == target_x and source_y == target_y:
            logging.info("Joy!")
            return True

        if total > 500:
            logging.info("Too many attempts")
            return False

        if walk_grid is None:
            start_x = min(source_x, target_x)
            end_x = max(source_x, target_x)
            start_y = min(source_y, target_y)
            end_y = max(source_y, target_y)

            walk_grid = self.grid[start_x:end_x+1, start_y:end_y+1]
            walk_grid[:] = Tiles.DEEP_WATER

            source_x -= start_x
            source_y -= start_y

            target_x -= start_x
            target_y -= start_y

        if overwrite or (self.grid[source_x, source_y] == Tiles.EMPTY or self.grid[source_x, source_y] in BLOCKING_TILES):
            walk_grid[source_x, source_y] = tile

        moves = self.getPossibleMoves(source_x, source_y, previous_x, previous_y, walk_grid)

        if (len(moves) < 1):
            logging.info("out of moves")
            return False

        previous_x = source_x
        previous_y = source_y

        distances = []
        for x, y in moves:
            distance = self.distanceBetween(x, y, target_x, target_y)
            #if distance == 1:
            #    logging.info("Within 1 space", total)
            #    return True
            distances.append((distance, (x,y)))

        distances.sort(key = operator.itemgetter(0))

        idx = 0
        if (len(distances) > 1):
            idx = randint(0,1)

        source_x, source_y = distances[idx][1]

        if source_x == target_x and source_y == target_y:
            logging.info("Joy!")
            return True

        total += 1
        return self.boundedDrunkenWalk(source_x, source_y, target_x, target_y, previous_x, previous_y, total, tile, walk_grid, overwrite)

    def drunkenWalk(self, source_x, source_y, target_x, target_y, previous_x = None, previous_y = None, total = 0, tile = Tiles.CAVERN_FLOOR, overwrite = False):
        if source_x == target_x and source_y == target_y:
            return True

        if total > 500:
            logging.info("Too many attempts")
            return False

        if overwrite or (self.grid[source_x, source_y] == Tiles.EMPTY or self.grid[source_x, source_y] in BLOCKING_TILES):
            self.grid[source_x, source_y] = tile

        moves = self.getPossibleMoves(source_x, source_y, previous_x, previous_y, check_carve = False)

        if (len(moves) < 1):
            logging.info("out of moves")
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

        self.drunkenWalk(x1,y1,x2,y2,tile=Tiles.SHALLOW_WATER, overwrite = True)

    def DeepWater(self):
        tiles = np.where(self.grid == Tiles.SHALLOW_WATER)

        water_grid = self.grid.copy()
        for idx, x in enumerate(tiles[0]):
            y = tiles[1][idx]

            surrounding = surrounding_tiles(x,y,self.grid)
            surrounding_water = np.where(surrounding == Tiles.SHALLOW_WATER)

            if len(surrounding_water[0]) == 9:
                water_grid[x,y] = Tiles.DEEP_WATER

        self.grid[:] = water_grid[:]

    def validateMap(self):
        stairs = np.where(self.grid == Tiles.STAIRS_FLOOR)

        if len(stairs[0]) < 2:
            logging.info("Not enough exits")
            return False

        walkable = self.grid.copy()
        mask = np.isin(self.grid, [Tiles.OBSTACLE, Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL, Tiles.DEEP_WATER, Tiles.IMPENETRABLE])
        walkable[mask] = 0

        astar = tcod.path.AStar(walkable, 0)
        path = astar.get_path(stairs[0][0], stairs[1][0], stairs[0][1], stairs[1][1])

        if len(path) < 1:
            logging.info("Can't route between stairs")
            return False
        #elif len(path) < 30:
        #    logging.info("Path between stairs too short")
        #    return False

        return True
