import tcod
import tcod.event
import numpy as np

from bestiary import create_player
from entities.character import Character
from components.health import Health
from etc.enum import RoutingOptions, Species, Tiles

#from map_objects.dungeonGenerator import dungeonGenerator
#from map_objects.level_map import LevelMap
from map_objects.np_dungeonGeneration import dungeonGenerator, random_walk
from map_objects.np_level_generation import arena, levelOneGenerator, levelGenerator, bossLevelGenerator, roomsLevel, cavernLevel, squares, cavernRoomsLevel
from map_objects.np_level_map import LevelMap
from etc.colors import COLORS
from etc.configuration import CONFIG
from etc.enum import Tiles
from utils.utils import matprint
from render_functions import get_names_under_mouse

from random import choice, randint, randrange

from etc.exceptions import MapError, MapGenerationFailedError, RoomOutOfBoundsError

class MainMenu(tcod.event.EventDispatch):
    def __init__(self):
        self.motion = tcod.event.MouseMotion()
        self.lbut = self.mbut = self.rbut = 0
        self.map_console = tcod.console.Console(CONFIG.get('map_width'), CONFIG.get('map_height'), 'F')
        self.player = Character(None, '@', 'player', tcod.dark_green, health=Health(30),
                               species=Species.PLAYER)
        self.player.x = 10
        self.player.y = 10

        self.current_level = None
        self.uncon = np.zeros((CONFIG.get('map_width'), CONFIG.get('map_height')), dtype=np.int8)
        self.dijkstra = np.zeros((CONFIG.get('map_width'), CONFIG.get('map_height')), dtype=np.int8)

        self.showUnnconnected = False
        self.showDijskra = False
        self.roomsize = 3

        self.map_type = 1

        self.create_map()

        CONFIG['debug'] = True

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

        under_mouse_text = get_names_under_mouse(self.motion.tile.x, self.motion.tile.y, self.current_level)
        text_height = root_console.get_height_rect(1, 0, root_console.width - 2, 10, under_mouse_text)

        root_console.print_box(
            1,
            CONFIG.get('info_panel_y') - text_height - 1,
            root_console.width - 2,
            text_height,
            under_mouse_text,
            fg=tcod.white,
            bg=None,
            alignment=tcod.LEFT,
        )

    def ev_keydown(self, event: tcod.event.KeyDown):
        if event.sym == ord('['):
            print("Toggling showDijskra")
            self.showDijskra = not self.showDijskra
        elif event.sym == ord(']'):
            print("Toggling unconnected")
            self.showUnnconnected = not self.showUnnconnected
        if event.sym == ord('-'):
            self.roomsize -= 1
            self.create_map()
        elif event.sym == ord('='):
            self.roomsize += 1
            self.create_map()
        elif event.sym == ord('r'):
            self.create_map()
        elif event.sym == ord('1'):
            self.map_type = 1
            self.create_map()
        elif event.sym == ord('2'):
            self.map_type = 2
            self.create_map()
        elif event.sym == ord('3'):
            self.map_type = 3
            self.create_map()
        elif event.sym == ord('4'):
            self.map_type = 4
            self.create_map()
        elif event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

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
        self.make_map()
        return
        while not valid:
            print('Map Attempt: ' + str(count))
            valid = self.make_map()
            count += 1

    def make_map(self):
        try:
            x = 15
            y = 15

            dm = dungeonGenerator(CONFIG.get('map_width'), CONFIG.get('map_height'))

            if self.map_type == 1:
                dm = levelOneGenerator(CONFIG.get('map_width'), CONFIG.get('map_height'))
            elif self.map_type == 2:
                cavernLevel(dm, x, y)
            elif self.map_type == 3:
                cavernRoomsLevel(dm, x, y)
            elif self.map_type == 4:
                roomsLevel(dm, x, y)

            self.current_level = LevelMap(dm.grid, dm.rooms)

            return True
        except (MapError, RoomOutOfBoundsError) as e:
            print("="*30)
            print(e)
            print("="*30)
            self.make_map()

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
