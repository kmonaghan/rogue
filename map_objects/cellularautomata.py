class CellularAutomata:
	'''
	Rather than implement a traditional cellular automata, I
	decided to try my hand at a method discribed by "Evil
	Scientist" Andy Stobirski that I recently learned about
	on the Grid Sage Games blog.
	'''
	def __init__(self):
		self.level = []

		self.iterations = 30000
		self.neighbors = 4 # number of neighboring walls for this cell to become a wall
		self.wallProbability = 0.50 # the initial probability of a cell becoming a wall, recommended to be between .35 and .55

		self.ROOM_MIN_SIZE = 16 # size in total number of cells, not dimensions
		self.ROOM_MAX_SIZE = 500 # size in total number of cells, not dimensions

		self.smoothEdges = True
		self.smoothing =  1

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.caves = []

		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self.randomFillMap(mapWidth,mapHeight)

		self.createCaves(mapWidth,mapHeight)

		self.getCaves(mapWidth,mapHeight)

		self.connectCaves(mapWidth,mapHeight)

		self.cleanUpMap(mapWidth,mapHeight)
		return self.level

	def randomFillMap(self,mapWidth,mapHeight):
		for y in range (1,mapHeight-1):
			for x in range (1,mapWidth-1):
				#print("(",x,y,") = ",self.level[x][y])
				if random.random() >= self.wallProbability:
					self.level[x][y] = 0

	def createCaves(self,mapWidth,mapHeight):
		# ==== Create distinct caves ====
		for i in xrange (0,self.iterations):
			# Pick a random point with a buffer around the edges of the map
			tileX = random.randint(1,mapWidth-2) #(2,mapWidth-3)
			tileY = random.randint(1,mapHeight-2) #(2,mapHeight-3)

			# if the cell's neighboring walls > self.neighbors, set it to 1
			if self.getAdjacentWalls(tileX,tileY) > self.neighbors:
				self.level[tileX][tileY] = 1
			# or set it to 0
			elif self.getAdjacentWalls(tileX,tileY) < self.neighbors:
				self.level[tileX][tileY] = 0

		# ==== Clean Up Map ====
		self.cleanUpMap(mapWidth,mapHeight)

	def cleanUpMap(self,mapWidth,mapHeight):
		if (self.smoothEdges):
			for i in xrange (0,5):
				# Look at each cell individually and check for smoothness
				for x in range(1,mapWidth-1):
					for y in range (1,mapHeight-1):
						if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x,y) <= self.smoothing):
							self.level[x][y] = 0

	def createTunnel(self,point1,point2,currentCave,mapWidth,mapHeight):
		# run a heavily weighted random Walk
		# from point1 to point1
		drunkardX = point2[0]
		drunkardY = point2[1]
		while (drunkardX,drunkardY) not in currentCave:
			# ==== Choose Direction ====
			north = 1.0
			south = 1.0
			east = 1.0
			west = 1.0

			weight = 1

			# weight the random walk against edges
			if drunkardX < point1[0]: # drunkard is left of point1
				east += weight
			elif drunkardX > point1[0]: # drunkard is right of point1
				west += weight
			if drunkardY < point1[1]: # drunkard is above point1
				south += weight
			elif drunkardY > point1[1]: # drunkard is below point1
				north += weight

			# normalize probabilities so they form a range from 0 to 1
			total = north+south+east+west
			north /= total
			south /= total
			east /= total
			west /= total

			# choose the direction
			choice = random.random()
			if 0 <= choice < north:
				dx = 0
				dy = -1
			elif north <= choice < (north+south):
				dx = 0
				dy = 1
			elif (north+south) <= choice < (north+south+east):
				dx = 1
				dy = 0
			else:
				dx = -1
				dy = 0

			# ==== Walk ====
			# check colision at edges
			if (0 < drunkardX+dx < mapWidth-1) and (0 < drunkardY+dy < mapHeight-1):
				drunkardX += dx
				drunkardY += dy
				if self.level[drunkardX][drunkardY] == 1:
					self.level[drunkardX][drunkardY] = 0

	def getAdjacentWallsSimple(self, x, y): # finds the walls in four directions
		wallCounter = 0
		#print("(",x,",",y,") = ",self.level[x][y])
		if (self.level[x][y-1] == 1): # Check north
			wallCounter += 1
		if (self.level[x][y+1] == 1): # Check south
			wallCounter += 1
		if (self.level[x-1][y] == 1): # Check west
			wallCounter += 1
		if (self.level[x+1][y] == 1): # Check east
			wallCounter += 1

		return wallCounter

	def getAdjacentWalls(self, tileX, tileY): # finds the walls in 8 directions
		pass
		wallCounter = 0
		for x in range (tileX-1, tileX+2):
			for y in range (tileY-1, tileY+2):
				if (self.level[x][y] == 1):
					if (x != tileX) or (y != tileY): # exclude (tileX,tileY)
						wallCounter += 1
		return wallCounter

	def getCaves(self, mapWidth, mapHeight):
		# locate all the caves within self.level and stor them in self.caves
		for x in range (0,mapWidth):
			for y in range (0,mapHeight):
				if self.level[x][y] == 0:
					self.floodFill(x,y)

		for set in self.caves:
			for tile in set:
				self.level[tile[0]][tile[1]] = 0

		# check for 2 that weren't changed.
		'''
		The following bit of code doesn't do anything. I
		put this in to help find mistakes in an earlier
		version of the algorithm. Still, I don't really
		want to remove it.
		'''
		for x in range (0,mapWidth):
			for y in range (0,mapHeight):
				if self.level[x][y] == 2:
					print("(",x,",",y,")")

	def floodFill(self,x,y):
		'''
		flood fill the separate regions of the level, discard
		the regions that are smaller than a minimum size, and
		create a reference for the rest.
		'''
		cave = set()
		tile = (x,y)
		toBeFilled = set([tile])
		while toBeFilled:
			tile = toBeFilled.pop()

			if tile not in cave:
				cave.add(tile)

				self.level[tile[0]][tile[1]] = 1

				#check adjacent cells
				x = tile[0]
				y = tile[1]
				north = (x,y-1)
				south = (x,y+1)
				east = (x+1,y)
				west = (x-1,y)

				for direction in [north,south,east,west]:

					if self.level[direction[0]][direction[1]] == 0:
						if direction not in toBeFilled and direction not in cave:
							toBeFilled.add(direction)

		if len(cave) >= self.ROOM_MIN_SIZE:
			self.caves.append(cave)

	def connectCaves(self, mapWidth, mapHeight):
		# Find the closest cave to the current cave
		for currentCave in self.caves:
			for point1 in currentCave: break # get an element from cave1
			point2 = None
			distance = None
			for nextCave in self.caves:
				if nextCave != currentCave and not self.checkConnectivity(currentCave,nextCave):
					# choose a random point from nextCave
					for nextPoint in nextCave: break # get an element from cave1
					# compare distance of point1 to old and new point2
					newDistance = self.distanceFormula(point1,nextPoint)
					if (newDistance < distance) or distance == None:
						point2 = nextPoint
						distance = newDistance

			if point2: # if all tunnels are connected, point2 == None
				self.createTunnel(point1,point2,currentCave,mapWidth,mapHeight)

	def distanceFormula(self,point1,point2):
		d = sqrt( (point2[0]-point1[0])**2 + (point2[1]-point1[1])**2)
		return d

	def checkConnectivity(self,cave1,cave2):
		# floods cave1, then checks a point in cave2 for the flood

		connectedRegion = set()
		for start in cave1: break # get an element from cave1

		toBeFilled = set([start])
		while toBeFilled:
			tile = toBeFilled.pop()

			if tile not in connectedRegion:
				connectedRegion.add(tile)

				#check adjacent cells
				x = tile[0]
				y = tile[1]
				north = (x,y-1)
				south = (x,y+1)
				east = (x+1,y)
				west = (x-1,y)

				for direction in [north,south,east,west]:

					if self.level[direction[0]][direction[1]] == 0:
						if direction not in toBeFilled and direction not in connectedRegion:
							toBeFilled.add(direction)

		for end in cave2: break # get an element from cave2

		if end in connectedRegion: return True

		else: return False
