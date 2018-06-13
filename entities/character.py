__metaclass__ = type

import libtcodpy as libtcod

import game_state
import screenrendering

from entities.object import Object

from components.level import Level

from render_order import RenderOrder

class Character(Object):
    def __init__(self, point, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, gear=None, level=None):
        super(Character, self).__init__(point, char, name, color, blocks, always_visible, fighter, ai, item, gear)
        self.inventory = []
        self.level = Level()
        if self.level:
            self.level.owner = self

        self.render_order = RenderOrder.ACTOR

    def get_equipped_in_slot(self, slot):  #returns the equipment in a slot, or None if it's empty
        for obj in self.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def get_all_equipped(self):  #returns a list of equipped items
        equipped_list = []
        for item in self.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list

    def add_to_inventory(self, obj):
        obj.owner = self
        self.inventory.append(obj)

    def remove_from_inventory(self, obj):
        self.inventory.remove(obj)
        obj.owner = None

    def list_quests(self):
        titles = []
        if len(game_state.active_quests) == 0:
            titles = [['No active quests.', libtcod.white]]
        else:
            for quest in game_state.active_quests:
                titles.append([quest.title, libtcod.white])

        index = screenrendering.menu("Quests", titles, screenrendering.INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(game_state.active_quests) == 0: return None

        messageconsole.message(quest.title, libtcod.white)
        messageconsole.message(quest.description, libtcod.white)

    def completed_quest(self, quest):
        if (self.fighter is not None):
            self.level.add_xp(quest.xp)
