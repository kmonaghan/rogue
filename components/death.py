from game_messages import Message

from components.naming import Naming

from etc.colors import COLORS
from etc.enum import GameStates, RenderOrder, Species

import pubsub

class BasicDeath:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self):
        self.rotting_time = 50
        self.rotting = False
        self.skeletal = False

    def npc_death(self, game_map):
        if self.owner.health and self.owner.health.on_death:
            print(">>>>>>>On death trigger")
            self.owner.health.on_death(self.owner)
            return GameStates.PLAYER_TURN

        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        self.owner.char = '%'
        self.owner.color = COLORS.get('corpse')
        #self.owner.species = Species.CORPSE
        self.owner.ai = None
        self.owner.render_order = RenderOrder.CORPSE

        for item in self.owner.inventory.items:
            if (item.lootable):
                item.x = self.owner.x
                item.y = self.owner.y
                #npc.inventory.drop_item(item)
                game_map.current_level.add_entity(item)

        game_map.current_level.remove_entity(self.owner)
        self.owner.blocks = False
        game_map.current_level.add_entity(self.owner)

        self.rotting = True

        self.owner.add_component(Naming(self.owner.base_name, prefix='Rotting corpse of'), 'naming')

        return GameStates.PLAYER_TURN

    def decompose(self, game_map):
        self.rotting_time -= 1

        if (self.rotting_time <= 0):
            game_map.current_level.remove_entity(self.owner)
        elif (self.rotting_time <= 25) and not self.skeletal:
            self.skeletonize()

    def skeletonize(self):
        self.rotting = False
        self.skeletal = True
        self.rotting_time = 24
        self.owner.color = COLORS.get('skeletal')
        self.owner.naming.prefix = 'Skeletal remains of'

class WarlordDeath(BasicDeath):
    def npc_death(self, game_map):
        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        game_state = super(WarlordDeath, self).npc_death(game_map)

        return GameStates.GAME_COMPLETE

class PlayerDeath(BasicDeath):
    def npc_death(self, game_map):

        self.owner.char = '%'
        self.owner.color = COLORS.get('corpse')
        self.owner.blocks = False
        self.owner.render_order = RenderOrder.CORPSE
        pubsub.pubsub.add_message(pubsub.Publish(None, pubsub.PubSubTypes.MESSAGE, message = Message('You died!', COLORS.get('failure_text'))))

        return GameStates.GAME_OVER
