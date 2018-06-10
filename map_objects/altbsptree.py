import libtcodpy as libtcod

import random

from map_objects.leaf import Leaf
from map_objects.point import Point
from map_objects.room import Room
from map_objects.tile import Tile

class AltBSPTree:
	def __init__(self):
		self.bsp = None
		self.DEPTH = 10
		self.MIN_SIZE = 5
		self.FULL_ROOMS = False
		self.mapWidth = 0
		self.mapHeight = 0
		self.level = []
		self.rooms = []

	def generateLevel(self, mapWidth, mapHeight):
		self.level = [[Tile(True) for y in range(mapHeight)] for x in range(mapWidth)]

		self.mapWidth = mapWidth
		self.mapHeight = mapHeight

        #New root node
		self.bsp = libtcod.bsp_new_with_size(0, 0, self.mapWidth, self.mapHeight)

        #Split into nodes
		libtcod.bsp_split_recursive(self.bsp, 0, self.DEPTH, self.MIN_SIZE + 1, self.MIN_SIZE + 1, 1.5, 1.5)

        #Traverse the nodes and create rooms
		libtcod.bsp_traverse_inverted_level_order(self.bsp, self.traverse_node)

		return self.level

	def traverse_node(self, node, dat):
		#Create rooms
		if libtcod.bsp_is_leaf(node):
			minx = node.x + 1
			maxx = node.x + node.w - 1
			miny = node.y + 1
			maxy = node.y + node.h - 1

			if maxx == self.mapWidth - 1:
				maxx -= 1
			if maxy == self.mapHeight - 1:
				maxy -= 1

			#If it's False the rooms sizes are random, else the rooms are filled to the node's size
			if self.FULL_ROOMS == False:
				minx = libtcod.random_get_int(None, minx, maxx - self.MIN_SIZE + 1)
				miny = libtcod.random_get_int(None, miny, maxy - self.MIN_SIZE + 1)
				maxx = libtcod.random_get_int(None, minx + self.MIN_SIZE - 2, maxx)
				maxy = libtcod.random_get_int(None, miny + self.MIN_SIZE - 2, maxy)

			node.x = minx
			node.y = miny
			node.w = maxx-minx + 1
			node.h = maxy-miny + 1

			room = Room(minx, miny, maxx - minx, maxy - miny)

			#Dig room
			for x in range(minx, maxx + 1):
				for y in range(miny, maxy + 1):
					self.level[x][y].blocked = False
					self.level[x][y].block_sight = False

			self.rooms.append(room)

        #Create corridors
		else:
			left = libtcod.bsp_left(node)
			right = libtcod.bsp_right(node)
			node.x = min(left.x, right.x)
			node.y = min(left.y, right.y)
			node.w = max(left.x + left.w, right.x + right.w) - node.x
			node.h = max(left.y + left.h, right.y + right.h) - node.y

			if node.horizontal:
				if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
					x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
					x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
					y = libtcod.random_get_int(None, left.y + left.h, right.y)
					self.vline_up(x1, y - 1)
					self.hline(x1, y, x2)
					self.vline_down(x2, y + 1)

				else:
					minx = max(left.x, right.x)
					maxx = min(left.x + left.w - 1, right.x + right.w - 1)
					x = libtcod.random_get_int(None, minx, maxx)

					# catch out-of-bounds attempts
					while x > self.mapWidth - 1:
						x -= 1

					self.vline_down(x, right.y)
					self.vline_up(x, right.y - 1)

			else:
				if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
					y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
					y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
					x = libtcod.random_get_int(None, left.x + left.w, right.x)
					self.hline_left(x - 1, y1)
					self.vline(x, y1, y2)
					self.hline_right(x + 1, y2)
				else:
					miny = max(left.y, right.y)
					maxy = min(left.y + left.h - 1, right.y + right.h - 1)
					y = libtcod.random_get_int(None, miny, maxy)

					# catch out-of-bounds attempts
					while y > self.mapHeight - 1:
						y -= 1

					self.hline_left(right.x - 1, y)
					self.hline_right(right.x, y)

		return True

	def vline(self, x, y1, y2):
		if y1 > y2:
			y1,y2 = y2,y1

		for y in range(y1,y2+1):
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False

	def vline_up(self, x, y):
		while y >= 0 and self.level[x][y].blocked == True:
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False
			y -= 1

	def vline_down(self, x, y):
		while y < self.mapHeight and self.level[x][y].blocked == True:
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False
			y += 1

	def hline(self, x1, y, x2):
		if x1 > x2:
			x1,x2 = x2,x1

		for x in range(x1,x2+1):
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False

	def hline_left(self, x, y):
		while x >= 0 and self.level[x][y].blocked == True:
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False
			x -= 1

	def hline_right(self, x, y):
		while x < self.mapWidth and self.level[x][y].blocked == True:
			self.level[x][y].blocked = False
			self.level[x][y].block_sight = False
			x += 1
