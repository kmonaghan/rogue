import libtcodpy as libtcod

import equipment

from components.ai import BasicNPC
from components.ai import Hatching
from components.ai import Hunter

from components.fighter import Fighter

from entities.animal import Animal

from map_objects.point import Point

from species import Species

class Snake(Animal):
    def __init__(self, point = None):
        char = 'S'
        name = "Snake"
        color = libtcod.darker_gray
        always_visible = False
        blocks = True
        fighter = Fighter(hp=5, defense=1, power=1, xp=2)
        ai = Hunter(attacked_ai = BasicNPC(), hunting = Species.RAT)
        item = None
        gear = None
        species = Species.SNAKE

        super(Snake, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)

        teeth = equipment.teeth()
        teeth.lootable = False

        self.inventory.add_item(teeth)
        self.equipment.toggle_equip(teeth)

        self.egg_generation = 0

    def onKill(self, npc, game_map):
        if (npc.species == Species.RAT):
            self.egg_generation += 1

        if (self.egg_generation > 2):
            self.egg_generation = 0

            egg = SnakeEgg(Point(self.x, self.y))

            game_map.add_npc_to_map(egg)

class SnakeEgg(Animal):
    def __init__(self, point):
        char = 'E'
        name = "Snake Egg"
        color = libtcod.darker_gray
        always_visible = False
        blocks = True
        fighter = Fighter(hp=2, defense=3, power=0, xp=0)
        ai = Hatching(Snake())
        item = None
        gear = None
        species = Species.SNAKE

        super(SnakeEgg, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)
