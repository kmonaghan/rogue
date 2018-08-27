import libtcodpy as libtcod

from game_messages import Message

from game_states import GameStates

from render_functions import RenderOrder

def player_death(player):
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died!', libtcod.red), GameStates.PLAYER_DEAD

def warlord_death(npc, entities):

    return npc_death(npc, entities)
