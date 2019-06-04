import tcod
import tcod.event
import numpy as np

from bestiary import create_player
from entities.character import Character
from components.health import Health
from etc.enum import RoutingOptions, Species, Tiles

#from map_objects.dungeonGenerator import dungeonGenerator
#from map_objects.level_map import LevelMap
from map_objects.np_dungeonGeneration import dungeonGenerator
from map_objects.np_level_map import LevelMap
from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.enum import Tiles
from utils.utils import matprint
from render_functions import get_names_under_mouse

from random import choice, randint, randrange

class MainMenu(tcod.event.EventDispatch):
    def __init__(self):
        self.motion = tcod.event.MouseMotion()
        self.lbut = self.mbut = self.rbut = 0
        self.map_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')
        self.player = Character(None, '@', 'player', tcod.dark_green, health=Health(30),
                               species=Species.PLAYER)

        self.current_level = None
        self.uncon = np.zeros((CONFIG.get('map_width'), CONFIG.get('map_height')), dtype=np.int8)
        self.dijkstra = np.zeros((CONFIG.get('map_width'), CONFIG.get('map_height')), dtype=np.int8)

        self.showUnnconnected = False
        self.showDijskra = False
        self.roomsize = 3

        self.create_map()

    def on_enter(self):
        tcod.sys_set_fps(60)

    def on_draw(self):
        #---------------------------------------------------------------------
        # Blit the subconsoles to the main console and flush all rendering.
        #---------------------------------------------------------------------
        root_console.clear(fg=COLORS.get('console_background'))

        self.current_level.update_and_draw_all(self.map_console, self.player)
        '''
        for x in range(CONFIG.get('map_width')):
            self.map_console.ch[x, 0] = x

        for x in range(CONFIG.get('map_width')):
            self.map_console.ch[x, 1] = x + CONFIG.get('map_width')

        for x in range(CONFIG.get('map_width')):
            self.map_console.ch[x, 2] = x + CONFIG.get('map_width') + CONFIG.get('map_width')
        '''

        if self.showUnnconnected:
            for (x,y), value in np.ndenumerate(self.uncon):
                self.map_console.ch[x, y] = ord(str(int(value % 10)))

        if self.showDijskra:
            for (x,y), value in np.ndenumerate(self.dijkstra):
                self.map_console.ch[x, y] = ord(str(int(value % 10)))

        self.map_console.blit(root_console, 0, 0, 0, 0,
                                  self.map_console.width, self.map_console.height)

        root_console.print(1, CONFIG.get('panel_y') - 1, get_names_under_mouse(self.motion.tile.x, self.motion.tile.y, self.current_level), tcod.white)

    def ev_keydown(self, event: tcod.event.KeyDown):
        if event.sym == ord('['):
            self.showDijskra = not self.showDijskra
        elif event.sym == ord(']'):
            self.showUnnconnected = not self.showUnnconnected
        if event.sym == ord('-'):
            self.roomsize -= 1
            self.create_map()
        elif event.sym == ord('='):
            self.roomsize += 1
            self.create_map()
        elif event.sym == ord('r'):
            self.create_map()

    def ev_mousemotion(self, event: tcod.event.MouseMotion):
        self.motion = event

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown):
        if event.button == tcod.event.BUTTON_LEFT:
            self.lbut = True
        elif event.button == tcod.event.BUTTON_MIDDLE:
            self.mbut = True
        elif event.button == tcod.event.BUTTON_RIGHT:
            self.rbut = True

    def ev_mousebuttonup(self, event: tcod.event.MouseButtonUp):
        if event.button == tcod.event.BUTTON_LEFT:
            self.lbut = False
        elif event.button == tcod.event.BUTTON_MIDDLE:
            self.mbut = False
        elif event.button == tcod.event.BUTTON_RIGHT:
            self.rbut = False

    def ev_quit(self, event: tcod.event.Quit):
        raise SystemExit()

    def create_map(self):
        valid = False
        count = 1
        while not valid:
            print('Map Attempt: ' + str(count))
            valid = self.make_map()
            count += 1

    def make_map(self):
        dm = dungeonGenerator(CONFIG.get('map_width'), CONFIG.get('map_height'))

        #dm.addCircleShapedRoom(10,10,radius=self.roomsize, add_door = False, add_walls = True)
        #dm.placeRandomRooms(3, 15, 2, 2, 500, add_door = True, add_walls = True)
        '''
        for i in range (5):
            x, y = dm.findEmptySpace()

            if not x and not y:
                continue
            else:
                dm.generateCorridors(x = x, y = y)
        '''
        #dm.connectDoors()

        #dm.cleanUpMap()

        dm.generateCaves(46, 3)
        dm.removeAreasSmallerThan(35)

        #self.uncon = dm.findUnconnectedAreas()

        #dm.turnAreasSmallerThanIntoWater(min_size = 100)

        #dm.waterFeature()

        #dm.placeWalls()

        self.current_level = LevelMap(dm.grid)

        print ('Done generating')

        return True

        dm.generateCaves(46, 3)

        dm.removeAreasSmallerThan(35)

        self.uncon = dm.findUnconnectedAreas()

        dm.joinUnconnectedAreas(self.uncon, connecting_tile = Tiles.CAVERN_FLOOR)

        dm.waterFeature()

        dm.waterFeature()

        '''
        0 = top
        1 = right side
        2 = bottom
        3 = left side
        '''

        side = randint(0, 3)

        if side == 0:
            x = randint(1, CONFIG.get('map_width') - 4)
            y = 1
        elif side == 1:
            x = CONFIG.get('map_width') - 4
            y = randint(0, CONFIG.get('map_height') - 4)
        elif side == 2:
            x = randint(1, CONFIG.get('map_width') - 4)
            y = CONFIG.get('map_height') - 4
        elif side == 3:
            x = 1
            y = randint(1, CONFIG.get('map_height') - 4)

        dm.addRoom(x,y,3,3, overlap = True, add_walls = True)

        dm.grid[x+1,y+1] = Tiles.STAIRSFLOOR

        _, self.dijkstra = dm.create_dijkstra_map(x+1,y+1, avoid = [Tiles.CAVERN_WALL, Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL, Tiles.DEEPWATER])

        max = np.amax(self.dijkstra)

        min = (max // 3) * 2

        min_distance = randint(min, max)

        possible_positions = np.where(self.dijkstra[0:CONFIG.get('map_width') - 4,0:CONFIG.get('map_height') - 4] >= min_distance)

        if (len(possible_positions) < 1):
            print('Nowhere to place exit')
            return False

        attempts = 0

        possible_tuples = list(zip(possible_positions[0],possible_positions[1]))

        placed = False

        while len(possible_tuples) > 1:
            idx = randint(0, len(possible_tuples)-1)

            x, y = possible_tuples[idx]

            print('Attempting to place at: ' + str(x) + ',' + str(y))
            placed = dm.addRoom(x,y,3,3, overlap = True, add_walls = True)

            if placed:
                dm.grid[x+1,y+1] = Tiles.STAIRSFLOOR
                possible_tuples = []
            else:
                attempts += 1
                print('Room place attempt: ' + str(attempts))
                del possible_tuples[idx]

        if not placed:
            print('Failed to place exit')
            return False

        dm.placeWalls()

        dm.grid[0] = Tiles.CAVERN_WALL
        dm.grid[-1] = Tiles.CAVERN_WALL
        dm.grid[:, 0] = Tiles.CAVERN_WALL
        dm.grid[:, -1] = Tiles.CAVERN_WALL

        if not dm.validateMap():
            return False

        self.current_level = LevelMap(dm.grid)

        print('Map is good')

        return True

def main():
    global current_game, root_console

    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )

    root_console = tcod.console_init_root(CONFIG.get('full_screen_width'),
                                            CONFIG.get('full_screen_height'),
                                            CONFIG.get('window_title'), False, order='F')
    map_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')

    current_game = MainMenu()

    while not tcod.console_is_window_closed():
        current_game.on_draw()
        tcod.console_flush()
        handle_events()

def handle_events():
    for event in tcod.event.get():
        current_game.dispatch(event)

if __name__ == "__main__":
    main()
