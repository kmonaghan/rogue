import logging

import tcod

from etc.enum import LevelUp
from random import choice

#experience and level-ups
LEVEL_UP_BASE = 100
LEVEL_UP_FACTOR = 1.5

class Level:
    def __init__(self, current_level=1, current_xp=0, level_up_base=LEVEL_UP_BASE, level_up_factor=LEVEL_UP_FACTOR, xp_value=0):
        self.current_level = current_level
        self.current_xp = current_xp

        self.next_level_xp = level_up_base
        self.level_up_factor = level_up_factor

        self.current_level_xp = 0

        self.xp_value = xp_value

    def __str__(self):
        return f"{self.current_level} ({self.current_xp}/{self.experience_to_next_level})"

    def __repr__(self):
        return f"{self.current_level} ({self.current_xp}/{self.experience_to_next_level})"

    @property
    def experience_to_next_level(self):
        return self.current_level_xp + self.next_level_xp

    def xp_worth(self, npc):
        logging.info(f"Getting xp value for {self.owner} to give to {npc}")

        earned_xp = self.xp_value

        level_difference = self.owner.level.current_level - npc.level.current_level

        if (level_difference < -4):
            earned_xp = 0
        elif (level_difference < 0):
            earned_xp = int(earned_xp * ((5 - abs(level_difference)) / 5))
        elif (level_difference > 0):
            earned_xp = int(earned_xp * (1 + ((5 - abs(level_difference)) / 5)))

        return earned_xp

    def add_xp(self, xp):
        self.current_xp += xp

    def can_level_up(self):
        if self.current_xp >= self.experience_to_next_level:
            return True

        return False

    def level_up_stats(self, choice = LevelUp.HEALTH):
        self.current_level += 1
        self.current_level_xp += self.next_level_xp
        self.next_level_xp = int(self.next_level_xp * self.level_up_factor)

        if choice == LevelUp.HEALTH:
            self.owner.health.base_max_hp += 20
            self.owner.health.hp += 20
        elif choice == LevelUp.STRENGTH:
            self.owner.offence.base_power += 1
        elif choice == LevelUp.DEFENCE:
            self.owner.defence.base_defence += 1

        self.owner.health.hp = self.owner.health.max_hp

    def random_level_up(self, total_levels):
        if (total_levels < 1):
            return

        for _ in range(total_levels):
            self.level_up_stats(choice(list(LevelUp)))
