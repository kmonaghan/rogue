import libtcodpy as libtcod
import equipment
import messageconsole
import pc

class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.death_function = death_function
        self.multiplier = 1
        self.owner = None

    @property
    def power(self):  #return actual power, by summing up the bonuses from all equipped items
        bonus = sum(equipment.power_bonus for equipment in self.owner.get_all_equipped())
        return (self.base_power + bonus) * self.multiplier

    @property
    def defense(self):  #return actual defense, by summing up the bonuses from all equipped items
        bonus = sum(equipment.defense_bonus for equipment in self.owner.get_all_equipped())
        return (self.base_defense + bonus) * self.multiplier

    @property
    def max_hp(self):  #return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_hp_bonus for equipment in self.owner.get_all_equipped())
        return (self.base_max_hp + bonus) * self.multiplier

    def attack(self, target):
        #a simple formula for attack damage
        total = libtcod.random_get_int(0, 1, 20) + self.power
        hit = total - target.fighter.defense

        if hit > 0:
            #make the target take some damage
            weapon = self.owner.get_equipped_in_slot("right hand")
            damage = weapon.damage()

            messageconsole.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            messageconsole.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

            #check for death. if there's a death function, call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

                if self.owner != pc.player:  #yield experience to the player
                    pc.player.fighter.xp += self.xp

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
