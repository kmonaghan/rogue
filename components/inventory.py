import tcod as libtcod

from game_messages import Message

from etc.enum import ResultTypes

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                ResultTypes.MESSAGE: Message('You cannot carry any more, your inventory is full.', libtcod.yellow)
            })
        else:
            results.append({
                ResultTypes.REMOVE_ENTITY: item,
                ResultTypes.MESSAGE: Message('{0} picked up the {1}.'.format(self.owner.name, item.name), libtcod.blue)
            })

            self.items.append(item)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({ResultTypes.DROP_ITEM_FROM_INVENTORY: item})

        return results

    def examine_item(self, item):
        results = []
        return item.examine()

    def search(self, name=None):
        if name:
            return filter(lambda x: x.name == name, self.items)

        return None
