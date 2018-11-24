import libtcodpy as libtcod
import equipment
import quest

from equipment_slots import EquipmentSlots
from game_messages import Message

class Fighter:
    #combat-related properties and methods (npc, player, NPC).
    def __init__(self, xp):
        self.xp = xp
        self.owner = None

    def take_damage(self, amount, npc = None):
        results = []

        self.owner.health.take_damage(amount)

        if self.owner.health.dead:
            earned_xp = self.xp

            if (npc):
                level_difference = self.owner.level.current_level - npc.level.current_level

                if (level_difference < -4):
                    earned_xp = 0
                elif (level_difference < 0):
                    earned_xp = int(earned_xp * ((5 - abs(level_difference)) / 5))
                elif (level_difference > 0):
                    earned_xp = int(earned_xp * (1 + ((5 - abs(level_difference)) / 5)))

            results.append({'dead': self.owner, 'xp': earned_xp})

        self.owner.hasBeenAttacked(npc)

        return results
