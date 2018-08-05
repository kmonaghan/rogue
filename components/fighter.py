import libtcodpy as libtcod
import equipment
import game_state
import quest

from equipment_slots import EquipmentSlots
from game_messages import Message

class Fighter:
    #combat-related properties and methods (npc, player, NPC).
    def __init__(self, hp, defense, power, xp):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.multiplier = 1
        self.owner = None

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus

    def attack(self, target):
        results = []

        #a simple formula for attack damage
        total = libtcod.random_get_int(0, 1, 20)
        multiplier = 1;
        if (total == 20):
            multiplier = 2

        total = total + self.power
        hit = total - target.fighter.defense

        if (hit > 0) or (multiplier == 2):
            #make the target take some damage
            weapon = self.owner.equipment.get_equipped_in_slot(EquipmentSlots.MAIN_HAND)
            damage = weapon.equippable.damage() * multiplier

            msg = self.owner.name.capitalize() + ' attacks ' + target.name + ' with ' + weapon.name + ' for ' + str(damage) + ' hit points.'
            if (multiplier == 2):
                msg = self.owner.name.capitalize() + ' smashes ' + target.name + ' with a massive blow from their ' + weapon.name + ' for ' + str(damage) + ' hit points.'

            results.append({'message': Message(msg, libtcod.white)})
            results.extend(target.fighter.take_damage(damage, self.owner))
        else:
            results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name), libtcod.white)})

        return results

    def take_damage(self, amount, npc = None):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})

        self.owner.hasBeenAttacked(npc)

        return results

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def display_color(self):
        healthpercent = (self.hp * 100) / self.max_hp
        if (healthpercent <=20):
            return libtcod.red
        elif (healthpercent <=60):
            return libtcod.orange
        elif (healthpercent <=80):
            return libtcod.yellow

        return self.owner.color
