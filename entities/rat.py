import libtcodpy as libtcod

from random import randint

import equipment

from components.ai import BasicNPC, Hunter, SpawnNPC, ScreamerNPC

from components.health import Health
from components.fighter import Fighter

from entities.animal import Animal

from map_objects.point import Point

from species import Species

class RatOld(Animal):
    def __init__(self, point = None):
        char = 'R'
        name = 'Rat'
        color = libtcod.darker_gray
        always_visible = False
        blocks = True
        rat_health = Health(4)
        fighter = Fighter(xp=2)
        ai = Hunter(attacked_ai = BasicNPC(), hunting = Species.EGG)
        item = None
        gear = None
        species = Species.RAT

        super(Rat, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species, health=rat_health)

        teeth = equipment.teeth()
        teeth.lootable = False

        self.inventory.add_item(teeth)
        self.equipment.toggle_equip(teeth)

class RatNest(Animal):
    def __init__(self, point = None, dungeon_level = 1):
        char = 'N'
        name = 'Rat Nest'
        color = libtcod.red
        always_visible = False
        blocks = True
        fighter = Fighter(xp=2)
        health = Health(4)
        ai = SpawnNPC(Rat)
        item = None
        gear = None
        species = Species.RATNEST

        super(RatNest, self).__init__(point, char, name, color, always_visible, blocks, fighter, ai, item, gear, species, health=health)

        potion = equipment.random_potion(dungeon_level = dungeon_level)
        potion.lootable = True

        self.inventory.add_item(potion)

    def hasBeenAttacked(self, npc):
        #print("Override hasBeenAttacked")
        health = (self.health.hp * 100.0) / self.health.max_hp
        print("health: " + str(health))
        if (health < 90):
            self.setAI(ScreamerNPC(Species.RAT))

        scream = 0
        if (health < 30):
            spawn_chance = 5
            self.ai.alert_range = 3
        elif (health < 60):
            spawn_chance = 7
            self.ai.alert_range = 2
        elif (health < 90):
            spawn_chance = 9

        spawn = randint(1, 10)

        if (spawn >= spawn_chance):
            #npc = Rat(self.point)
            print("Would spawn rat")
