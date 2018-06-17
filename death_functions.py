import libtcodpy as libtcod

from game_messages import Message

from game_states import GameStates

from render_functions import RenderOrder

def npc_death(npc, entities):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    death_message = Message('{0} is dead!'.format(npc.name.capitalize()), libtcod.orange)

    npc.char = '%'
    npc.color = libtcod.dark_red
    npc.blocks = False
    npc.fighter = None
    npc.ai = None
    npc.name = 'remains of ' + npc.name
    npc.render_order = RenderOrder.CORPSE

    for item in npc.inventory.items:
        if (item.lootable):
            npc.inventory.drop_item(item)
            entities.append(item)

    return death_message

def player_death(player):
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died!', libtcod.red), GameStates.PLAYER_DEAD

def warlord_death(npc, entities):

    return npc_death(npc, entities)
