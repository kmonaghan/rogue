from random import randint

from components.poisoned import Poisoned
from components.speed import Speed

from etc.colors import COLORS
from etc.enum import DamageType, MessageType, ResultTypes

from game_messages import Message

from map_objects.point import Point

from utils.random_utils import die_roll
from utils.utils import random_adjacent

class Ablity:
    def __init__(self, name = ""):
        self.owner = None
        self.name = name

    def __str__(self):
        return f"{self.__class__} {self.name}"

    def __repr__(self):
        return f"{self.__class__} {self.name}"

    def on_equip(self, source):
        pass

    def on_attack(self, source, target, game_map):
        pass

    def on_defend(self, source, target, game_map):
        pass

    def on_dequip(self, source):
        pass

class Defence(Ablity):
    def __init__(self, name = "Defence", defence=0):
        super().__init__(name=name)
        self.defence = defence

    def on_equip(self, source):
        pass
        #source.defence.equipment_defence += self.defence

    def on_dequip(self, source):
        pass
        #source.defence.equipment_defence -= self.defence

class Poisoning(Ablity):
    def __init__(self, chance_to_poison=50, damage_per_turn=1, duration=1):
        super().__init__(name="Poisoning")
        self.chance_to_poison = chance_to_poison
        self.damage_per_turn = damage_per_turn
        self.duration = duration

    def on_attack(self, source, target, game_map):
        results = []

        if randint(1, 100) > self.chance_to_poison:
            poison = Poisoned(self.damage_per_turn, self.duration, source)
            target.add_component(poison, 'poisoned')
            results.extend(poison.start())

        return results

class Power(Ablity):
    def __init__(self, name = "Power", power=0):
        super().__init__(name=name)
        self.power = power

    def on_equip(self, source):
        pass

    def on_dequip(self, source):
        pass

class PushBack(Ablity):
    def __init__(self, distance=3, damage=10, chance=75):
        super().__init__(name="PushBack")
        self.distance = distance
        self.damage = damage
        self.chance = chance

    def on_attack(self, source, target, game_map):
        results = []

        if randint(1,100) < self.chance:
            return results

        spaces = randint(1,self.distance)
        dx = target.x - source.x
        dy = target.y - source.y

        for _ in range(spaces):
            results.extend([{ResultTypes.MOVE_FORCE: (target, dx, dy, self.damage)}])

        return results

class ExtraDamage(Ablity):
    def __init__(self, number_of_dice=1, type_of_dice=6, name="extra", damage_type=DamageType.DEFAULT):
        super().__init__(name="Damage")
        self.number_of_dice = number_of_dice
        self.type_of_dice = type_of_dice
        self.name = name
        self.damage_type = damage_type

    def on_attack(self, source, target, game_map):
        results = []

        damage = die_roll(self.number_of_dice, self.type_of_dice)
        damage_results, total_damage = target.health.take_damage(damage, source, self.damage_type)
        if total_damage > 0:
            msg = Message(f"{target.name} takes {str(damage)} {self.name} total_damage.", COLORS.get('damage_text'), source=source, target=target, type=MessageType.EFFECT)
            results.extend(damage_results)
            results.extend([{ResultTypes.MESSAGE: msg}])

        return results

class LifeDrain(Ablity):
    def __init__(self, number_of_dice=1, type_of_dice=6, chance=50, transfer=0.5):
        super().__init__(name="Draining")
        self.chance = chance
        self.number_of_dice = number_of_dice
        self.type_of_dice = type_of_dice
        self.transfer = transfer

    def on_attack(self, source, target, game_map):
        results = []

        damage = die_roll(self.number_of_dice, self.type_of_dice)
        damage_results, total_damage = target.health.take_damage(damage, source, DamageType.DEFAULT)
        if total_damage > 0:
            drain_amount = max(1, int(total_damage * self.transfer))
            msg = Message(f"{target.name} takes {str(damage)} {self.name} damage.", COLORS.get('damage_text'), source=source, target=target, type=MessageType.EFFECT)
            results.extend(damage_results)
            results.extend([{ResultTypes.MESSAGE: msg}])
            results.extend(source.health.heal(drain_amount))

        return results

class Infection(Ablity):
    def __init__(self, name="Infection", chance=50, on_turn=None, on_death=None):
        super().__init__(name=name)
        self.chance = chance
        self.on_turn = on_turn
        self.on_death = on_death

    def on_attack(self, source, target, game_map):
        results = []

        if randint(1,100) < self.chance:
            return results
        if self.on_death:
            target.health.on_death = self.on_death

        return results

class Paralysis(Ablity):
    def __init__(self, name="Paralysis", chance=50, turns_paralysed = 2):
        super().__init__(name=name)
        self.chance = chance
        self.turns_paralysed = turns_paralysed

    def on_attack(self, source, target, game_map):
        results = []

        if randint(1,100) < self.chance:
            return results

        target.energy.current_energy = -(target.energy.act_energy * self.turns_paralysed)
        msg = Message(f"{target.name} is paralysed for {self.turns_paralysed} turns.", COLORS.get('damage_text'), source=source, target=target, type=MessageType.EFFECT)
        results.extend([{ResultTypes.MESSAGE: msg}])

        return results

class Speed(Ablity):
    def __init__(self, name = "Speed", act_energy_adjustment=0.5):
        super().__init__(name=name)
        self.act_energy_adjustment = act_energy_adjustment
        self.old_speed = None

    def on_equip(self, source):
        self.old_speed = source.speed
        source.add_component(Speed(act_energy_adjustment=self.act_energy_adjustment, duration=-1, damage_on_end=False), 'speed')

    def on_dequip(self, source):
        source.speed = self.old_speed

class Spawning(Ablity):
    def __init__(self, name = "Spawning", maker=None):
        super().__init__(name=name)
        self.maker = maker

    def on_attack(self, source, target, game_map):
        pass

    def on_defend(self, source, target, game_map):
        results = []

        x, y = random_adjacent((source.x, source.y))

        if (game_map.current_level.walkable[x, y] and not game_map.current_level.blocked[x, y]):
            entity = self.maker(Point(x, y))
            entity.ai.set_target(source)

            results = [{ResultTypes.ADD_ENTITY: entity}]

            if source.children:
                source.children.addChild(entity)

        return results

class SpellAbility(Ablity):
    def __init__(self, name="", spell=None, number_of_dice=0, type_of_dice=0, radius=3, targets_inventory=False, chance=50):
        super().__init__(name=name)
        self.chance = chance
        self.number_of_dice = number_of_dice
        self.radius = radius
        self.spell = spell
        self.type_of_dice = type_of_dice
        self.targets_inventory = targets_inventory

    def on_attack(self, source, target, game_map):
        results = []

        if not target and self.targets_inventory:
            results.append({ResultTypes.TARGET_ITEM_IN_INVENTORY: source})
        else:
            results = self.spell(game_map=game_map,
                                        caster=source,
                                        target=target,
                                        number_of_dice=self.number_of_dice,
                                        type_of_dice=self.type_of_dice,
                                        radius=self.radius)
        return results
