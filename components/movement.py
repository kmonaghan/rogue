import logging

import tcod

from random import choice

from etc.enum import RoutingOptions

from map_objects.point import Point

class Movement:
        def __init__(self, can_move=True):
            self.can_move = can_move
            self.routing_avoid = [RoutingOptions.AVOID_BLOCKERS]
            self.has_moved = False
            self.last_move = None

        def move(self, dx, dy, current_level):
            if not self.can_move:
                return

            if not current_level.within_bounds(self.owner.x + dx, self.owner.y + dy):
                logging.info(f"{self.owner.name} {self.owner.point} attempted to move out of bounds: {self.owner.x + dx} {self.owner.y + dy}")
                return

            #move by the given amount, if the destination is not blocked
            if current_level.walkable[self.owner.x + dx, self.owner.y + dy] and not current_level.blocked[self.owner.x + dx, self.owner.y + dy]:
                self.place(self.owner.x + dx, self.owner.y + dy, current_level)

                return True
            else:
                logging.info(f"{self.owner.name} can't move as blocked")

                return False

        def place(self, x, y, current_level):
            self.last_move = self.owner.point
            self.has_moved = True
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
            if game_map.current_level.walkable[target_point.x, target_point.y] and not game_map.current_level.blocked[target_point.x, target_point.y]:
                self.place(target_point.x, target_point.y, game_map.current_level)

                return True

            return False

        def move_to_random_adjacent(self, game_map):
            """Move the owner to a random adjacent tile."""
            dx, dy = choice([
                (-1, 1), (0, 1), (1, 1),
                (-1, 0),         (1, 0),
                (-1, -1), (0, -1), (1, -1)])
            self.attempt_move(Point(self.owner.x + dx, self.owner.y + dy), game_map)
