import random
from math import sqrt

import game_state

from map_objects.point import Point
from map_objects.rect import Rect
from map_objects.room import Room
from map_objects.tile import Tile

class MazeWithRooms:
	'''
	Python implimentation of the rooms and mazes algorithm found at
	http://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/
	by Bob Nystrom
	'''
	def __init__(self):
		self.level = []
		self.rooms = []
		self.prefabs = []

		self.ROOM_MAX_SIZE = 10
		self.ROOM_MIN_SIZE = 5

		self.buildRoomAttempts = 200
		self.connectionChance = 0.04
		self.windingPercent = 0.1
		self.allowDeadEnds = False

	def add_prefab(self, prefab):
		self.prefabs.append(prefab)

	def generateLevel(self, mapWidth, mapHeight, max_rooms, room_min_size, room_max_size):
		self.ROOM_MAX_SIZE = room_max_size
		self.ROOM_MIN_SIZE = room_min_size

		# The level dimensions must be odd
		self.level = [[Tile(True)
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		if (mapWidth % 2 == 0): mapWidth -= 1
		if (mapHeight % 2 == 0): mapHeight -= 1

		self._regions = [[ None
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._currentRegion = -1 # the index of the current region in _regions

		if (len(self.prefabs) > 0):
			self.add_prefab_room(mapWidth,mapHeight)

		self.addRooms(mapWidth,mapHeight)#?

		# Fill in the empty space around the rooms with mazes
		for y in range (1,mapHeight,2):
			for x in range(1,mapWidth,2):
				if not self.level[x][y].blocked:
					continue
				start = (x,y)
				self.growMaze(start,mapWidth,mapHeight)

		self.connectRegions(mapWidth,mapHeight)

		if not self.allowDeadEnds:
			self.removeDeadEnds(mapWidth,mapHeight)

		if (len(self.prefabs) > 0):
			for prefab in self.prefabs:
				prefab.carve(self.level)

		return self.level

	def growMaze(self,start,mapWidth,mapHeight):
		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		cells = []
		lastDirection = None

		self.startRegion()
		self.carve(start[0],start[1])

		cells.append(start)

		while cells:
			cell = cells[-1]

			# see if any adjacent cells are open
			unmadeCells = set()

			'''
			north = (0,-1)
			south = (0,1)
			east = (1,0)
			west = (-1,0)
			'''
			for direction in [north,south,east,west]:
				if self.canCarve(cell,direction,mapWidth,mapHeight):
					unmadeCells.add(direction)

			if (unmadeCells):
				'''
				Prefer to carve in the same direction, when
				it isn't necessary to do otherwise.
				'''
				if ((lastDirection in unmadeCells) and
					(random.random() > self.windingPercent)):
					direction = lastDirection
				else:
					direction = unmadeCells.pop()

				newCell = ((cell[0]+direction[0]),(cell[1]+direction[1]))
				self.carve(newCell[0],newCell[1])

				newCell = ((cell[0]+direction[0]*2),(cell[1]+direction[1]*2))
				self.carve(newCell[0],newCell[1])
				cells.append(newCell)

				lastDirection = direction

			else:
				# No adjacent uncarved cells
				cells.pop()
				lastDirection = None

	def add_prefab_room(self,mapWidth,mapHeight):
		for prefab in self.prefabs:

			x = (random.randint(0,mapWidth-prefab.room.w-1)/2)*2+1
			y = (random.randint(0,mapHeight-prefab.room.h-1)/2)*2+1

			prefab.room.change_xy(x,y)

			failed = False
			for otherRoom in self.rooms:
				if prefab.room.intersect(otherRoom):
					failed = True

					break

			if not failed:
				self.rooms.append(prefab.room)
				self.startRegion()
				self.createRoom(prefab.room)

	def addRooms(self,mapWidth,mapHeight):

		for i in range(self.buildRoomAttempts):

			'''
			Pick a random room size and ensure that rooms have odd
			dimensions and that rooms are not too narrow.
			'''
			roomWidth = random.randint(int(self.ROOM_MIN_SIZE/2),int(self.ROOM_MAX_SIZE/2))*2+1
			roomHeight = random.randint(int(self.ROOM_MIN_SIZE/2),int(self.ROOM_MAX_SIZE/2))*2+1
			x = (random.randint(0,mapWidth-roomWidth-1)/2)*2+1
			y = (random.randint(0,mapHeight-roomHeight-1)/2)*2+1

			room = Room(x,y,roomWidth,roomHeight)
			# check for overlap with previous rooms
			failed = False
			for otherRoom in self.rooms:
				if room.intersect(otherRoom):
					failed = True
					if (game_state.debug):
						game_state.objects.remove(room.room_detail)
					break

			if not failed:
				self.rooms.append(room)
				self.startRegion()
				self.createRoom(room)

	def connectRegions(self,mapWidth,mapHeight):
		# Find all of the tiles that can connect two regions
		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		connectorRegions = [[ None
			for y in xrange(mapHeight)]
				for x in xrange(mapWidth)]

		for x in xrange(1,mapWidth-1):
			for y in xrange(1,mapHeight-1):
				if self.level[x][y].blocked == False: continue

				# count the number of different regions the wall tile is touching
				regions = set()
				for direction in [north,south,east,west]:
					newX = x + direction[0]
					newY = y + direction[1]
					region = self._regions[newX][newY]
					if region != None:
						regions.add(region)

				if (len(regions) < 2): continue

				# The wall tile touches at least two regions
				connectorRegions[x][y] = regions

		# make a list of all of the connectors
		connectors = set()
		for x in xrange(0,mapWidth):
			for y in xrange(0,mapHeight):
				if connectorRegions[x][y]:
					connectorPosition = (x,y)
					connectors.add(connectorPosition)

		# keep track of the regions that have been merged.
		merged = {}
		openRegions = set()
		for i in xrange(self._currentRegion+1):
			merged[i] = i
			openRegions.add(i)

		# connect the regions
		while len(openRegions) > 1:
			# get random connector
			#connector = connectors.pop()
			for connector in connectors: break

			# carve the connection
			self.addJunction(connector)

			# merge the connected regions
			x = connector[0]
			y = connector[1]

			# make a list of the regions at (x,y)
			regions = []
			for n in connectorRegions[x][y]:
				# get the regions in the form of merged[n]
				actualRegion = merged[n]
				regions.append(actualRegion)

			dest = regions[0]
			sources = regions[1:]

			'''
			Merge all of the effective regions. You must look
			at all of the regions, as some regions may have
			previously been merged with the ones we are
			connecting now.
			'''
			for i in xrange(self._currentRegion+1):
				if merged[i] in sources:
					merged[i] = dest

			# clear the sources, they are no longer needed
			for s in sources:
				openRegions.remove(s)

			# remove the unneeded connectors
			toBeRemoved = set()
			for pos in connectors:
				# remove connectors that are next to the current connector
				if self.distance(connector,pos) < 2:
					# remove it
					toBeRemoved.add(pos)
					continue

				regions = set()
				x = pos[0]
				y = pos[1]
				for n in connectorRegions[x][y]:
					actualRegion = merged[n]
					regions.add(actualRegion)
				if len(regions) > 1:
					continue

				if random.random() < self.connectionChance:
					self.addJunction(pos)

				# remove it
				if len(regions) == 1:
					toBeRemoved.add(pos)

			connectors.difference_update(toBeRemoved)

	def createRoom(self, room):
		print room.describe()
		# set all tiles within a rectangle to 0
		for x in range(room.x1, room.x2):
			for y in range(room.y1, room.y2):
				self.carve(x,y)

	def addJunction(self,pos):
		self.level[pos[0]][pos[1]].setFloor()

	def removeDeadEnds(self,mapWidth,mapHeight):
		done = False

		north = (0,-1)
		south = (0,1)
		east = (1,0)
		west = (-1,0)

		while not done:
			done = True

			for y in xrange(1,mapHeight):
				for x in xrange(1,mapWidth):
					if not self.level[x][y].blocked:

						exits = 0
						for direction in [north,south,east,west]:
							if not self.level[x+direction[0]][y+direction[1]].blocked:
								exits += 1
						if exits > 1: continue

						done = False
						self.level[x][y].setWall()

	def canCarve(self,pos,dir,mapWidth,mapHeight):
		'''
		gets whether an opening can be carved at the location
		adjacent to the cell at (pos) in the (dir) direction.
		returns False if the location is out of bounds or if the cell
		is already open.
		'''
		x = pos[0]+dir[0]*3
		y = pos[1]+dir[1]*3

		if not (0 < x < mapWidth) or not (0 < y < mapHeight):
			return False

		x = pos[0]+dir[0]*2
		y = pos[1]+dir[1]*2

		# return True if the cell is a wall (1)
		# false if the cell is a floor (0)
		return (self.level[x][y].blocked)

	def distance(self,point1,point2):
		d = sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
		return d

	def startRegion(self):
		self._currentRegion += 1

	def carve(self,x,y):
		self.level[x][y].setFloor()
		self._regions[x][y] = self._currentRegion
