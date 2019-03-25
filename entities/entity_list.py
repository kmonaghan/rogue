import itertools

from entities.character import Character

class EntityList:
    """A data structure for contining all the entities in a current map.  This
    is designed to support two sets of operations:

      - Standard list methods: append, remove, and iteration.
      - Efficient lookup by position in the map.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.lst = []
        self.coordinate_map = {
            (i, j): [] for i, j in itertools.product(range(width), range(height))
        }

    def append(self, entity):
        self.lst.append(entity)
        self.coordinate_map[(entity.x, entity.y)].append(entity)

    def remove(self, entity):
        self.lst.remove(entity)
        self.coordinate_map[(entity.x, entity.y)].remove(entity)

    def update_position(self, entity, old_position, new_position):
        try:
            self.coordinate_map[old_position].remove(entity)
        except ValueError:
            print("Could not remove entity: " + entity.name)
        self.coordinate_map[new_position].append(entity)

    def get_entities_in_position(self, position):
        return self.coordinate_map[position]

    def __iter__(self):
        yield from self.lst

    def find_closest(self, point, species, max_distance=2):
        npc = None

        start_x = point.x - max_distance
        start_y = point.y - max_distance

        if (start_x < 0):
            start_x = 0

        if (start_y < 0):
            start_y = 0

        end_x = start_x + (max_distance * 2) + 1
        if (end_x > self.width):
            end_x = self.width

        end_y = start_y + (max_distance * 2) + 1
        if (end_y > self.height):
            end_y = self.height

        dist = max_distance + 1

        #print("Start looking from: (" + str(start_x) + ", " + str(start_y) +")")
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                #print ("checking " + str(x) + ", " + str(y))

                if (len(self.coordinate_map[(x, y)])):
                    for entity in self.coordinate_map[(x, y)]:
                        if (point.x == x) and (point.y == y):
                            continue
                        if isinstance(entity, Character) and (entity.species == species) and not entity.health.dead:
                            entity_distance = abs(x - point.x)
                            if (entity_distance < dist):
                                #print("FOUND!")
                                npc = entity
                #else:
                #    #print "no entites at " + str(x) + ", " + str(y)

        return npc
