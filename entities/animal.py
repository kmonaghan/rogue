import libtcodpy as libtcod

from components.ai import BasicNPC

from entities.character import Character

from species import Species

class Animal(Character):
    def __init__(self, point, char, name, color, always_visible=False, blocks=True, fighter=None, ai=None, item=None, gear=None, species=Species.NONDESCRIPT):
        super(Animal, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)

    def hasBeenAttacked(self, npc):
        if (npc.name == 'player'):
            self.setAI(BasicNPC())
