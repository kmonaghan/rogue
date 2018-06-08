import random

from map_objects.leaf import Leaf
from map_objects.point import Point
from map_objects.tile import Tile

class BSPTree:
	def __init__(self):
		self.level = []
		self.rooms = []
		self.room = None
		self.MAX_LEAF_SIZE = 24
		self.ROOM_MAX_SIZE = 10
		self.ROOM_MIN_SIZE = 6

	def generateLevel(self, mapWidth, mapHeight):
		# Creates an empty 2D array or clears existing array
		self.level = [[Tile(True)
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self._leafs = []

		rootLeaf = Leaf(1,1,mapWidth-2,mapHeight-2)
		self._leafs.append(rootLeaf)

		splitSuccessfully = True
		# loop through all leaves until they can no longer split successfully
		while (splitSuccessfully):
			splitSuccessfully = False
			for l in self._leafs:
				if (l.child_1 == None) and (l.child_2 == None):
					if ((l.width > self.MAX_LEAF_SIZE) or
					(l.height > self.MAX_LEAF_SIZE) or
					(random.random() > 0.8)):
						if (l.splitLeaf()): #try to split the leaf
							print "Split the leaf"
							self._leafs.append(l.child_1)
							self._leafs.append(l.child_2)
							splitSuccessfully = True

		rootLeaf.createRooms(self)

		return self.level

	def createRoom(self, room):
		self.rooms.append(room)

		#Dig room
		for x in range(room.x1, room.x2):
			for y in range(room.y1, room.y2):
				self.level[x][y].blocked = False
				self.level[x][y].block_sight = False

	def createHall(self, room1, room2):
		# connect two rooms by hallways
		point1 = room1.center()
		point2 = room2.center()

		print "Room centers " + point1.describe() + ' and ' + point2.describe()

		# 50% chance that a tunnel will start horizontally
		if random.randint(0,1) == 1:
			self.createHorTunnel(point1.x, point2.x, point1.y)
			self.createVirTunnel(point1.y, point2.y, point2.x)

		else: # else it starts virtically
			self.createVirTunnel(point1.y, point2.y, point1.x)
			self.createHorTunnel(point1.x, point2.x, point2.y)

	def createHorTunnel(self, x1, x2, y):
		for x in range(min(x1,x2),max(x1,x2)+1):
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False

	def createVirTunnel(self, y1, y2, x):
		for y in range(min(y1,y2),max(y1,y2)+1):
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False
