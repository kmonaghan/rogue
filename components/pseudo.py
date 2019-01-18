import tcod as libtcod

from game_messages import Message

from game_states import GameStates

class GameStates(Enum):
    SLEEPING = auto()
    ATTACKING = auto()
    BERSERKING = auto()
    EXPLORING = auto()
    RETREATING = auto()
    SLEEPING = auto()

class Pseudo:
    def __init__(self):
        self.curious = 0
        self.courage = 0
        self.aggression = 0
        self.current_state = SLEEPING

    def take_turn(self, target, fov_map, game_map):
        if self.current_state == SLEEPING:
            return []
        elif self.current_state == EXPLORING:
            return []
