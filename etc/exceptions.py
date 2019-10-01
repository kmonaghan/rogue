class MapError(Exception):
   """Base class for other exceptions"""
   pass

class BadMapError(MapError):
   """Raised when map misses some validity metric"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Map unplayable"
    super(BadMapError, self).__init__(msg)

class FailedToPlaceEntranceError(MapError):
   """Raised when entrance can't be placed"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Failed to place an entrance"
    super(FailedToPlaceEntranceError, self).__init__(msg)

class FailedToPlaceExitError(MapError):
   """Raised when exit can't be placed"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Failed to place an exit"
    super(FailedToPlaceExitError, self).__init__(msg)

class FailedToPlaceRoomError(MapError):
   """Raised when room is not placed on map"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Failed to place a room"
    super(FailedToPlaceRoomError, self).__init__(msg)

class RoomOutOfBoundsError(MapError):
   """Raised when room is at least partially out of map bounds"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Failed to place a room as it's out of bounds"
    super(RoomOutOfBoundsError, self).__init__(msg)

class RoomOverlapsError(MapError):
   """Raised when a room overlaps another feature"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Failed to place a room as it overlaps with another feature"
    super(RoomOverlapsError, self).__init__(msg)

class MapGenerationFailedError(MapError):
   """Raised when no valid map is produced"""
   def __init__(self, msg=None):
    if msg is None:
        # Set some default useful error message
        msg = "Map generation failed"
    super(MapGenerationFailedError, self).__init__(msg)
