import tcod as libtcod

from components.ai import BasicNPC

from entities.character import Character

from species import Species

class Animal(Character):
    def __init__(self, point, char, name, color, always_visible=False, blocks=True, ai=None, item=None, gear=None, species=Species.NONDESCRIPT, health=None):
        super(Animal, self).__init__(point, char, name, color, always_visible, blocks, ai, item, gear, species, health=health)

    def hasBeenAttacked(self, npc):
        if (npc.name == 'player'):
            self.add_component(BasicNPC(), "ai")
