import equipment

from components.defence import Defence
from components.health import Health
from components.locked import Locked

from entities.entity import Entity

from etc.colors import COLORS
from etc.enum import Interactions, RenderOrder

def door(point = None, locked=False):
    door = Entity(point, '+', 'door', COLORS.get('light_door'), health=Health(4),
                    blocks=False, interaction=Interactions.DOOR, animate=False,
                    always_visible=True, render_order=RenderOrder.STAIRS)

    door.add_component(Defence(defence = 1), 'defence')
    if locked:
        make_lockable(door, locked_character='X', unlocked_character='+')

    return door

def make_lockable(item, locked_character='X', unlocked_character='+'):
    item.blocks = True
    item.transparent = False
    item.add_component(Locked(requires_key=True,locked_character=locked_character, unlocked_character=unlocked_character), 'locked')
    item.char = locked_character

    return equipment.key(unlocks=item)
