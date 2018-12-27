import libtcodpy as libtcod

import pubsub

class Health:
    def __init__(self, hp):
        self.base_max_hp = hp
        self.hp = hp
        self.dead = False

    @property
    def health_percentage(self):
        return ((self.hp * 100) / self.max_hp)

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
            pubsub.pubsub.add_message(pubsub.Publish(self.owner, pubsub.PubSubTypes.DEATH, target=npc))

        if self.dead: 
            earned_xp = 0
            if hasattr(self.owner, 'level'):
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

        if (self.health_percentage <=20):
            return libtcod.red
        elif (self.health_percentage <=60):
            return libtcod.orange
        elif (self.health_percentage <=80):
            return libtcod.yellow

        return self.owner.color
