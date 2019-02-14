from enum import Enum, auto

debug = False

class GameStates(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_DEAD = auto()
    SHOW_INVENTORY = auto()
    DROP_INVENTORY = auto()
    TARGETING = auto()
    LEVEL_UP = auto()
    CHARACTER_SCREEN = auto()
    EXAMINE_INVENTORY = auto()
    SHOW_QUESTS = auto()
    QUEST_ONBOARDING = auto()
    GAME_COMPLETE = auto()
