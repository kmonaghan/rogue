import libtcodpy as libtcod

class Health:
    def __init__(self, hp):
        self.base_max_hp = hp
        self.hp = hp
        self.dead = False

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    def take_damage(self, amount, npc = None):
        results = []

        if (self.dead):
            return results

        self.hp -= amount
        if (self.hp <= 0):
            self.dead = True
            self.hp = 0

        if self.dead:
            earned_xp = self.owner.level.xp_worth(npc)

            results.append({'dead': self.owner, 'xp': earned_xp})

        self.owner.hasBeenAttacked(npc)

        return results

    def heal(self, amt):
        if (self.dead):
            return

        self.hp += amt
        if (self.hp > self.base_max_hp):
            self.hp = self.base_max_hp

    def display_color(self):
        healthpercent = (self.hp * 100) / self.max_hp
        if (healthpercent <=20):
            return libtcod.red
        elif (healthpercent <=60):
            return libtcod.orange
        elif (healthpercent <=80):
            return libtcod.yellow

        return self.owner.color
