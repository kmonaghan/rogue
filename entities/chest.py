import libtcodpy as libtcod

import equipment

from components.fighter import Fighter

from entities.character import Character

from species import Species

class Chest(Character):
    def __init__(self, point, dungeon_level = 1):
        char = "C"
        name = "Chest"
        color= libtcod.blue
        always_visible = False
        blocks = True
        fighter = Fighter(hp=10, defense=1, power=0, xp=0)
        ai = None
        item = None
        gear = None
        species = Species.INANIMATE

        super(Chest, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species)

        #TODO: Generate random loot in chest
        potion = equipment.random_potion()
        potion.lootable = True

        weapon = equipment.random_magic_weapon()
        weapon.lootable = True

        #print("Chest weapon: " + weapon.name)

        scroll = equipment.random_scroll(dungeon_level=dungeon_level)
        scroll.lootable = True

        self.inventory.add_item(potion)
        self.inventory.add_item(weapon)
        self.inventory.add_item(scroll)
