import game_state

from map_objects.point import Point

def is_blocked(point):
    #first test the map tile
#    if (game_state.debug):
#        print "Map size: " + str(len(game_state.map)) + " x " + str(len(game_state.map[0]))
#        print "Testing: " + point.describe()

    if game_state.map[point.x][point.y].blocked:
        return True

    #now check for any blocking objects
    for object in game_state.objects:
        if object.blocks and object.x == point.x and object.y == point.y:
            return True

    return False
