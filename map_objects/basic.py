import random
import game_state

from map_objects.room import Room
from map_objects.floor import Floor
from map_objects.wall import Wall

class Basic:
	def __init__(self):
		self.level = []
		self.rooms = []
		self.prefabs = []

	def add_prefab(self, prefab):
		self.prefabs.append(prefab)

	def add_prefab_room(self,mapWidth,mapHeight):
		for prefab in self.prefabs:

			x = (random.randint(0,mapWidth-prefab.room.w-1)/2)*2+1
			y = (random.randint(0,mapHeight-prefab.room.h-1)/2)*2+1

			prefab.room.change_xy(x,y)

			self.createRoom(prefab.room)
			self.rooms.append(prefab.room)

	def carve(self,x,y):
		self.level[x][y] = Floor()

	def createRoom(self, room):
		print room.describe()
		# set all tiles within a rectangle to 0
		for x in range(room.x1, room.x2):
			for y in range(room.y1, room.y2):
				self.carve(x,y)

	def generateLevel(self,mapWidth,mapHeight):
		self.level = [[Wall()
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		if (len(self.prefabs) > 0):
			self.add_prefab_room(mapWidth,mapHeight)

		for prefab in self.prefabs:
			prefab.carve(self.level)

		return self.level
