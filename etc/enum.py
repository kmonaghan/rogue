from enum import Enum, IntEnum, auto

#-----------------------------------------------------------------------------
# The various game states.
#
# The behaviour of the main game loop is governed by the value of the
# game_states variable, which must be one the values from this enumeration.
#.............................................................................
#
# ANIMATION_PLAYING:
#   An animation is currently playing.  Each tick of the game loop is used to
#   advance a frame in this animation.  All player and enemy actions are halted
#   until the animation completes.
# CURSOR_INPUT:
#   The selection cursor is currently displayed and under the users control.
#   All (other) player and enemy actions are halted until the user selects a
#   position on the map.
# DROP_INVENTORY:
#   The inventory screen is open for dropping items.
# ENEMY_TURN:
#   It is the enemy's turn to take action.
# EQUIP_INVENTORY:
#   The inventory screen is open for equipping items.
# PLAYER_TURN:
#   It is the player's turn to take action.
# SHOW_INVENTORY:
#   The inventory is open for using items.
#.............................................................................
class GameStates(Enum):
    #ANIMATION_PLAYING = auto()
    #CURSOR_INPUT = auto()
    CHARACTER_SCREEN = auto()
    ENEMY_TURN = auto()
    GAME_COMPLETE = auto()
    GAME_EXIT = auto()
    GAME_PAUSED = auto()
    GAME_START = auto()
    GAME_OVER = auto()
    INVENTORY_DROP = auto()
    INVENTORY_EXAMINE = auto()
    INVENTORY_SELECT = auto()
    INVENTORY_THROW = auto()
    INVENTORY_USE = auto()
    LEVEL_UP = auto()
    PLAYER_TURN = auto()
    PLAYER_SLEEP = auto()
    POST_PLAYER_TURN = auto()
    QUEST_LIST = auto()
    QUEST_ONBOARDING = auto()
    QUEST_RESPONSE = auto()
    TARGETING = auto()

# Game states that can be canceled out of.
CANCEL_STATES = {
    GameStates.CHARACTER_SCREEN, GameStates.GAME_PAUSED,
    GameStates.INVENTORY_DROP, GameStates.INVENTORY_EXAMINE,
    GameStates.INVENTORY_THROW, GameStates.INVENTORY_SELECT,
    GameStates.INVENTORY_USE, GameStates.QUEST_LIST,
    GameStates.QUEST_ONBOARDING, GameStates.TARGETING,}

# Game states where an inventory is displayed.
INVENTORY_STATES = {
        GameStates.INVENTORY_DROP, GameStates.INVENTORY_EXAMINE,
        GameStates.INVENTORY_THROW, GameStates.INVENTORY_SELECT,
        GameStates.INVENTORY_USE,}

# Game states accepting of user input.
INPUT_STATES = {
    GameStates.CHARACTER_SCREEN,
    GameStates.INVENTORY_DROP, GameStates.INVENTORY_EXAMINE,
    GameStates.INVENTORY_THROW, GameStates.INVENTORY_SELECT,
    GameStates.INVENTORY_USE,
    GameStates.LEVEL_UP,
    GameStates.QUEST_LIST, GameStates.GAME_PAUSED,
    GameStates.QUEST_LIST, GameStates.QUEST_ONBOARDING,
    GameStates.GAME_OVER, GameStates.GAME_COMPLETE}

class InputTypes(Enum):
    CHARACTER_SCREEN = auto()
    CLICK_LEFT = auto()
    CLICK_RIGHT = auto()
    DEBUG_OFF = auto()
    DEBUG_ON = auto()
    EXIT = auto()
    GAME_EXIT = auto()
    GAME_LOAD = auto()
    GAME_NEW = auto()
    GAME_RESET = auto()
    GAME_RESTART = auto()
    GAME_SAVE = auto()
    INVENTORY_DROP = auto()
    INVENTORY_EXAMINE = auto()
    INVENTORY_INDEX = auto()
    INVENTORY_THROW = auto()
    INVENTORY_USE = auto()
    LEVEL_UP = auto()
    MOVE = auto()
    PICKUP = auto()
    QUEST_INDEX = auto()
    QUEST_LIST = auto()
    QUEST_RESPONSE = auto()
    RELOAD_LEVEL = auto()
    SHOW_DIJKSTRA_PLAYER = auto()
    SHOW_DIJKSTRA_FLEE = auto()
    SLEEP = auto()
    TAKE_STAIRS = auto()
    TARGETING = auto()
    DOWN_LEVEL = auto()
    WAIT = auto()

# Game states for menu
GAME_MENU_STATES = {
    InputTypes.GAME_EXIT, InputTypes.GAME_LOAD,
    InputTypes.GAME_NEW, InputTypes.GAME_RESTART,
    InputTypes.GAME_SAVE}

class ResultTypes(Enum):
    """The various results of turn actions.

    The results of game actions, and their consequent effects on game state are
    enumerated by these catagories.

    The elements of this enum are used as dictionary keys in dictionaries
    returned from components responsible for processing in game actions and
    consequences. The values in these dictionries store the data needed to
    update the game state as a result.  In the main game loop, these
    dictionaries are added to a stack (either player_turn_results or
    enemy_turn_results) for processing.  Results are processed until the stack
    is empty.

    Enum Elements:
    --------------
    ADD_ENTITY: entity
        Add an entity to the game map.
    ADD_ITEM_TO_INVENTORY: (item, entity)
        Add an item to the entity's inventory.
    ANIMATION: (Animation type, ... other data needed for specific animation)
        Play an animation.
    CONFUSE: entity
        Put the entity in a confused state.
    CURSOR_MODE: boolean
        Enter cursor mode.
    DAMAGE: (entity, source, amount, elements)
        Deal damage to an entity of some elemental types.  Note that this
        damage is not immediately commited, instead it may be further processed
        due to defensive characteristics of teh target entity.  For commited
        damage, see the HARM result type.
    DEAD_ENTITY: entity
        An entity has died.
    DEATH_MESSAGE: Message object
        A message that the player has died.  TODO: Depreciate this.
    # TODO: Rename to CONSUME_ITEM
    DISCARD_ITEM: (entity, bool)
        The entity has or has not consumed an item.
    DOUBLE_SPEED: entity
        Double the entities speed for a duration of turns.
    END_TURN: bool
        End the player's turn.
    EQUIP: (equipable_entity, entity):
        Equip equipable_entity onto entity.
    EQUIP_INVENTORY: boolean
        Open the inventory for equipping items.
    FREEZE: entity
        Freeze an entity.
    ITEM_DROPPED: item
        The player has dropped an item.  TODO: We should be able to drop an
        item in a position.
    MESSAGE: message
        Display a game message in the message queue.
    MOVE:
        ...
    MOVE_TOWARDS: entity, target_x, target_y
        Attempt to move the entity towards the target.
    MOVE_RANDOM_ADJACENT: entity
        Attempt to move the entity to a random adjacent square.
    MOVE_TO_RANDOM_POSITION: entity
        Find a random avalable position on the map, and move the entity there.
    """
    # We need this enum to have an order, since there are certain turn results
    # that must be processed first.
    def __lt__(self, other):
        return self.value < other.value

    ADD_ENTITY = auto()
    ADD_ITEM_TO_INVENTORY = auto()
    CHANGE_SWIM_STAMINA = auto()
    CONFUSE = auto()
    COMMON_IDENT = auto()
    DAMAGE = auto()
    DEAD_ENTITY = auto()
    DEATH_MESSAGE = auto()
    DISCARD_ITEM = auto()
    DOUBLE_SPEED = auto()
    DROP_ITEM_FROM_INVENTORY = auto()
    END_TURN = auto()
    EQUIP = auto()
    EQUIP_ARMOR = auto()
    EQUIP_WEAPON = auto()
    EARN_XP = auto()
    FREEZE = auto()
    FOV_RECOMPUTE = auto()
    HARM = auto()
    INCREASE_ATTACK_POWER = auto()
    MESSAGE = auto()
    MOVE = auto()
    MOVE_FORCE = auto()
    MOVE_RANDOM_ADJACENT = auto()
    MOVE_TOWARDS = auto()
    MOVE_WITH_PATH = auto()
    MOVE_TO_RANDOM_POSITION = auto()
    RECHARGE_ITEM = auto()
    REMOVE_ARMOR = auto()
    REMOVE_ENTITY = auto()
    REMOVE_WEAPON = auto()
    RESTORE_PLAYER_INPUT = auto()
    TARGET_ITEM_IN_INVENTORY = auto()
    CANCEL_TARGET_ITEM_IN_INVENTORY = auto()
    TARGETING = auto()
    QUEST_ONBOARDING = auto()
    QUEST_CANCELLED = auto()
    SET_POSITION = auto()
    # This must be processed before any healing (which is passed as a DAMAGE
    # message).
    INCREASE_MAX_HP = 90
    # These two must be processed first!
    ANIMATION = 99
    CURSOR_MODE = 98

class RenderOrder(Enum):
    TERRAIN = auto()
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
    OVERLAY = auto()

class RoutingOptions(Enum):
    AVOID_BLOCKERS = auto()
    AVOID_FIRE = auto()
    AVOID_FOV = auto()
    AVOID_SHRUBS = auto()
    AVOID_STEAM = auto()

class Species(Enum):
    NONDESCRIPT = auto()
    GOBLIN = auto()
    ORC = auto()
    TROLL = auto()
    ANIMAL = auto()
    RAT = auto()
    SNAKE = auto()
    EGG = auto()
    RATNEST = auto()
    INANIMATE = auto()
    CREATURE = auto()
    BAT = auto()
    PLAYER = auto()
    CORPSE = auto()
    UNDEAD = auto()
    OOZE = auto()

class Tiles(IntEnum):
    EMPTY = 0
    OBSTACLE = auto()
    IMPENETRABLE = auto()
    CAVERN_WALL = auto()
    CORRIDOR_WALL = auto()
    ROOM_WALL = auto()
    DOOR = auto()
    INTERNAL_DOOR = auto()
    EXIT_DOOR = auto()
    DEADEND = auto()
    CAVERN_FLOOR = auto()
    FUNGAL_CAVERN_FLOOR = auto()
    POTENTIAL_CORRIDOR_FLOOR = auto()
    CORRIDOR_FLOOR = auto()
    ROOM_FLOOR = auto()
    SHALLOW_WATER = auto()
    DEEP_WATER = auto()
    STAIRS_FLOOR = auto()
    SPAWN_POINT = auto()

WALKABLE_TILES = {
    Tiles.INTERNAL_DOOR, Tiles.EXIT_DOOR,
    Tiles.DOOR, Tiles.CAVERN_FLOOR,
    Tiles.FUNGAL_CAVERN_FLOOR,
    Tiles.CORRIDOR_FLOOR, Tiles.ROOM_FLOOR,
    Tiles.SHALLOW_WATER, Tiles.DEEP_WATER,
    Tiles.STAIRS_FLOOR, Tiles.SPAWN_POINT}

BLOCKING_TILES = {
    Tiles.OBSTACLE, Tiles.CAVERN_WALL,
    Tiles.CORRIDOR_WALL, Tiles.ROOM_WALL,
    Tiles.DEEP_WATER, Tiles.IMPENETRABLE
}

SHIMMERING_TILES = [
    Tiles.SHALLOW_WATER, Tiles.DEEP_WATER]

class TreeStates(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

class LevelUp(Enum):
    HEALTH = auto()
    STRENGTH = auto()
    DEFENCE = auto()

class HealthStates(IntEnum):
    FULL = 100
    BARELY_INJURED = 80
    INJURED = 60
    BADLY_INJURED = 40
    NEAR_DEATH = 20

class StairOption(Enum):
    GOUP = auto()
    GODOWN = auto()
    EXIT = auto()
    NOSTAIR = auto()

class Interactions(Enum):
    NONE = auto()
    FOE = auto()
    FRIEND = auto()
    QUESTGIVER = auto()
    DOOR = auto()

class DamageType(Enum):
    DEFAULT = auto()
    BLUNT = auto()
    SHARP = auto()
    FIRE = auto()
    ICE = auto()
    ELECTRIC = auto()
    POISON = auto()

class EquipmentSlots(Enum):
    MAIN_HAND = auto()
    OFF_HAND = auto()
    HEAD = auto()
    CHEST = auto()
    RING = auto()
    LEFT_RING_FINGER = auto()
    RIGHT_RING_FINGER = auto()

class MessageType(Enum):
    SYSTEM = auto()
    EVENT = auto()
    EFFECT = auto()
    COMBAT = auto()
