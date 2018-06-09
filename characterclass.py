import libtcodpy as libtcod
import equipment
import game_state
import messageconsole
import pc
import screenrendering
import quest

#experience and level-ups
LEVEL_UP_BASE = 100
LEVEL_UP_FACTOR = 150

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
            weapon = self.owner.get_equipped_in_slot("right hand")
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

                if self.owner != pc.player:  #yield experience to the player
                    pc.player.fighter.xp += self.xp

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def check_level_up(self):
        #see if the player's experience is enough to level-up
        level_up_xp = LEVEL_UP_BASE + self.owner.level * LEVEL_UP_FACTOR
        if self.xp >= level_up_xp:
            #it is! level up and ask to raise some stats
            self.owner.level += 1
            self.xp -= level_up_xp
            messageconsole.message('Your battle skills grow stronger! You reached level ' + str(self.level) + '!', libtcod.yellow)

            choice = None
            while choice == None:  #keep asking until a choice is made
                choice = screenrendering.menu('Level up! Choose a stat to raise:\n',
                                                [['Constitution (+20 HP, from ' + str(self.max_hp) + ')',libtcod.white],
                                                ['Strength (+1 attack, from ' + str(self.power) + ')',libtcod.white],
                                                ['Agility (+1 defense, from ' + str(self.defense) + ')',libtcod.white]],
                                                screenrendering.LEVEL_SCREEN_WIDTH)

            if choice == 0:
                self.base_max_hp += 20
                self.hp += 20
            elif choice == 1:
                self.base_power += 1
            elif choice == 2:
                self.base_defense += 1

            self.hp = self.max_hp

class Questgiver:
    def __init__(self, quest):
        self.owner = None
        self.quest = quest
        self.quest.owner = self

    def start_quest(self):
        self.owner.char = "!"
        self.owner.color = libtcod.silver

    def return_to_giver(self):
        print "return_to_giver"
        self.owner.color = libtcod.gold
        self.owner.always_visible = True

    def completed_quest(self):
        self.owner.char = "Q"
        self.owner.color = libtcod.blue
        self.owner.always_visible = False
        game_state.active_quests.remove(self.quest)

    def talk(self, pc):
        if (self.quest.started == False):
            self.quest.start_quest(pc)
        elif (self.quest.completed):
            messageconsole.message('Well done!')
            pc.completed_quest(self.quest)
            self.completed_quest()
        else:
            messageconsole.message('Have you done it yet?')

    def change_state(Self):
            npc.char = '!'
            npc.color = libtcod.silver
