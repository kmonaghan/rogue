from components.defence import Defence
from components.health import Health
from components.locked import Locked

from entities.entity import Entity

from etc.colors import COLORS
from etc.enum import Interactions

def door(point = None):
    door = Entity(point, 'X', 'door', COLORS.get('light_door'), health=Health(4),
                    blocks=True, interaction=Interactions.DOOR)

    door.add_component(Defence(defence = 1), 'defence')
    door.add_component(Locked(requires_key=True), 'locked')

    return door
