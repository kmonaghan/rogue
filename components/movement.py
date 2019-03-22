import tcod

from etc.enum import RoutingOptions

from map_objects.point import Point

class Movement:
        def __init__(self, can_move=True):
            self.can_move = can_move
            self.routing_avoid = routing_avoid=[RoutingOptions.AVOID_BLOCKERS]

        def move(self, dx, dy, current_level):
            if not self.can_move:
                return

            if not current_level.within_bounds(self.owner.x + dx, self.owner.y + dy):
                print(self.owner.name + " " + str(self.owner.x) + " " + str(self.owner.y) + " attempt to move out of bounds: " + str(self.owner.x + dx) + " " + str(self.owner.y + dy))
                return

            #move by the given amount, if the destination is not blocked
            if current_level.walkable[self.owner.x + dx, self.owner.y + dy] and not current_level.blocked[self.owner.x + dx, self.owner.y + dy]:
                self.place(self.owner.x + dx, self.owner.y + dy, current_level)
            else:
                print("can't move as blocked")

        def place(self, x, y, current_level):
            print("placed: " + self.owner.name)
            current_level.move_entity(self.owner, Point(x, y))
            self.owner.x = x
            self.owner.y = y

        def move_towards(self, target_point, game_map):
            tx = target_point.x - self.owner.x
            ty = target_point.y - self.owner.y

            dx = tx
            dy = ty

            if (tx < 0):
                dx = -1
            elif (tx > 0):
                dx = 1

            if (ty < 0):
                dy = -1
            elif (ty > 0):
                dx = 1

            self.attempt_move(Point(self.owner.x + dx, self.owner.y + dy), game_map)

        def attempt_move(self, target_point, game_map):
            print("attempting to move " + self.owner.name + " from " + self.owner.point.describe() + " to " + target_point.describe())
            if game_map.current_level.walkable[target_point.x, target_point.y] and not game_map.current_level.blocked[target_point.x, target_point.y]:
                self.place(target_point.x, target_point.y, game_map.current_level)

                return True

            print("can't move " + self.owner.name)

            return False

        def move_astar(self, target, game_map):
            print("move_astar")

            walkable = game_map.current_level.make_walkable_array(self.routing_avoid)
            walkable[target.x, target.y] = True
            walkable[self.owner.x, self.owner.y] = True
            astar = tcod.path.AStar(walkable)

            path = astar.get_path(self.owner.x, self.owner.y, target.x, target.y)
            print(path)

            if len(path):
                self.place(path[0][0], path[0][1], game_map.current_level)
                game_map.current_level.paths.append(path)
            else:
                # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
                # it will still try to move towards the player (closer to the corridor opening)
                self.move_towards(target, game_map)
                game_map.current_level.path = None
