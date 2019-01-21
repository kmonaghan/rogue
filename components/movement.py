import tcod as libtcod

from map_objects.point import Point

class Movement:
        def __init__(self, can_move=True):
            self.can_move = can_move

        def move(self, dx, dy):
            if not self.can_move:
                return

            #move by the given amount, if the destination is not blocked
            #if not is_blocked(Point(self.x + dx, self.y + dy)):
            self.owner.x += dx
            self.owner.y += dy

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
            if not game_map.is_blocked(target_point, True):
                self.owner.x = target_point.x
                self.owner.y = target_point.y

                return True

            return False

        def move_astar(self, target, game_map):
            # Create a FOV map that has the dimensions of the map
            fov = libtcod.map_new(game_map.width, game_map.height)

            # Scan the current map each turn and set all the walls as unwalkable
            for y1 in range(game_map.height):
                for x1 in range(game_map.width):
                    libtcod.map_set_properties(fov, x1, y1, not game_map.map[x1][y1].block_sight,
                                               not game_map.map[x1][y1].blocked)

            # Scan all the objects to see if there are objects that must be navigated around
            # Check also that the object isn't self or the target (so that the start and the end points are free)
            # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
            for entity in game_map.entities:
                if entity.blocks and entity != self.owner and entity != target:
                    # Set the tile as a wall so it must be navigated around
                    libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

            # Allocate a A* path
            # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
            my_path = libtcod.path_new_using_map(fov, 1.41)

            # Compute the path between self's coordinates and the target's coordinates
            libtcod.path_compute(my_path, self.owner.x, self.owner.y, target.x, target.y)

            # Check if the path exists, and in this case, also the path is shorter than 25 tiles
            # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
            # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
            if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 100: #25:
                # Find the next coordinates in the computed full path
                x, y = libtcod.path_walk(my_path, True)
                if x or y:
                    # Set self's coordinates to the next path tile
                    self.owner.x = x
                    self.owner.y = y
            else:
                # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
                # it will still try to move towards the player (closer to the corridor opening)
                self.move_towards(target.point, game_map)

                # Delete the path to free memory
            libtcod.path_delete(my_path)
