import libtcodpy as libtcod
import equipment
import game_state
import messageconsole
import screenrendering
import quest

from equipment_slots import EquipmentSlots

class Fighter:
    #combat-related properties and methods (npc, player, NPC).
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
        total = libtcod.random_get_int(0, 1, 20)
        multiplier = 1;
        if (total == 20):
            multiplier = 2

        total = total + self.power
        hit = total - target.fighter.defense

        if (hit > 0) or (multiplier == 2):
            #make the target take some damage
            weapon = self.owner.get_equipped_in_slot(EquipmentSlots.MAIN_HAND)
            damage = weapon.damage() * multiplier

            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' with ' + weapon.owner.name + ' for ' + str(damage) + ' hit points.'
            if (multiplier == 2):
                msg = self.owner.name.capitalize() + ' smashes ' + target.name + ' with a massive blow from their ' + weapon.owner.name + ' for ' + str(damage) + ' hit points.'
            messageconsole.message(msg)
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

                if self.owner != game_state.player:  #yield experience to the player
                    game_state.player.level.add_xp(self.xp)

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
