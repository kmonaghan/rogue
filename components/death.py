import libtcodpy as libtcod

from game_messages import Message

from game_states import GameStates

from render_functions import RenderOrder

import pubsub

class BasicDeath:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self):
        self.rotting_time = 50
        self.rotting = False
        self.skeletal = False

    def npc_death(self, game_map):
        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        self.owner.char = '%'
        self.owner.color = libtcod.dark_red
        self.owner.blocks = False
        self.owner.ai = None
        self.owner.render_order = RenderOrder.CORPSE

        for item in self.owner.inventory.items:
            if (item.lootable):
                item.x = self.owner.x
                item.y = self.owner.y
                #npc.inventory.drop_item(item)
                game_map.add_entity_to_map(item)

        self.rotting = True

        return GameStates.ENEMY_TURN

    def decompose(self, game_map):
        self.rotting_time -= 1
        if (self.rotting_time == 0):
            game_map.remove_entity_from_map(self.owner)
        elif (self.rotting_time <= 25):
            self.skeletonize()

    def skeletonize(self):
        self.rotting = False
        self.skeletal = True
        self.rotting_time = 24
        self.owner.color = libtcod.white

class WarlordDeath(BasicDeath):
    def npc_death(self, game_map):
        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        game_state = super(WarlordDeath, self).npc_death(game_map)

        return Message('Victory is yours!', libtcod.gold), GameStates.GAME_COMPLETE

class PlayerDeath(BasicDeath):
    def npc_death(self, game_map):
        print("player death")

        self.owner.char = '%'
        self.owner.color = libtcod.dark_red
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('You died!', libtcod.red)))

        return GameStates.PLAYER_DEAD
