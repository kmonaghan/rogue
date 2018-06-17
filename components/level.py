import libtcodpy as libtcod

#experience and level-ups
LEVEL_UP_BASE = 100
LEVEL_UP_FACTOR = 150

class Level:
    def __init__(self, current_level=1, current_xp=0, level_up_base=LEVEL_UP_BASE, level_up_factor=LEVEL_UP_FACTOR):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor

    @property
    def experience_to_next_level(self):
        return self.level_up_base + self.current_level * self.level_up_factor

    def add_xp(self, xp):
        self.current_xp += xp

        if self.current_xp > self.experience_to_next_level:
            self.current_xp -= self.experience_to_next_level
            self.current_level += 1

            self.level_up()

            return True
        else:
            return False

    def level_up_stats(self, choice = 0):
        if choice == 0:
            self.owner.fighter.base_max_hp += 20
            self.owner.fighter.hp += 20
        elif choice == 1:
            self.owner.fighter.base_power += 1
        elif choice == 2:
            self.owner.fighter.base_defense += 1

        self.owner.fighter.hp = self.owner.fighter.max_hp

    def random_level_up(self, total_levels):
        for x in range(total_levels):
            print "Adding levels for " + self.owner.name + ": " + str(total_levels)
            choice = libtcod.random_get_int(0, 0, 2)
            self.level_up_stats(choice)
