import itertools
import logging

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
        try:
            self.lst.remove(entity)
            self.coordinate_map[(entity.x, entity.y)].remove(entity)
        except ValueError:
            logging.info(f"{entity} not found in list")

    def update_position(self, entity, old_position, new_position):
        try:
            self.coordinate_map[old_position].remove(entity)
        except ValueError:
            logging.info("Could not remove entity: " + entity.name)
        self.coordinate_map[new_position].append(entity)

    def get_entities_in_position(self, position):
        if position[0] < 0 or position[0] > self.width:
            return None
        if position[1] < 0 or position[1] > self.height:
            return None

        return self.coordinate_map[position]

    def __iter__(self):
        yield from self.lst

    def find_closest(self, point, species, radius=2):
        """Find all the closest entity of a species to a given point within a
        given radius.

        Parameters
        ----------
        point: Point
            Center point of the search
        species: etc.enum.Species
            Species that this entity will attempt to find.
        radius: int
            The radius to search within.

        Returns
        -------
        Entity or None
          A valid entity or None if none found.
        """
        entities = self.find_all_closest(point, species, radius)

        npc = None
        dist = radius + 1

        for entity in entities or []:
            if isinstance(entity, Character) and (entity.species == species) and not entity.health.dead:
                entity_distance = abs(entity.x - point.x)
                if (entity_distance < dist):
                    npc = entity
        return npc

    def find_all_closest(self, point, species, radius=2):
        """Find all the closest entities of a species to a given point within a
        given radius.

        Parameters
        ----------
        point: Point
            Center point of the search
        species: etc.enum.Species
            Species that this entity will attempt to find.
        radius: int
            The radius to search within.

        Returns
        -------
        npcs: [Entities]
          A list of all valid entities.
        """
        npcs = []

        start_x = max(0, point.x - radius)
        start_y = max(0, point.y - radius)

        end_x = min(self.width, start_x + (radius * 2) + 1)
        end_y = min(self.height, start_y + (radius * 2) + 1)

        dist = radius + 1

        #logging.info("Start looking from: (" + str(start_x) + ", " + str(start_y) +")")
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                #logging.info ("checking " + str(x) + ", " + str(y))

                if (len(self.coordinate_map[(x, y)])):
                    for entity in self.coordinate_map[(x, y)]:
                        if (point.x == x) and (point.y == y):
                            continue
                        if isinstance(entity, Character) and not entity.health.dead:
                            if species and (entity.species != species):
                                continue

                            entity_distance = abs(x - point.x)
                            if (entity_distance < dist):
                                #logging.info("FOUND!")
                                npcs.append(entity)
                #else:
                #    #logging.info "no entites at " + str(x) + ", " + str(y)

        return npcs

    def find_all_visible(self):
        visible = [x for x in self.lst if x.always_visible == True]

        return visible

    def find_all_of_type(self, entity_type):
        visible = [x for x in self.lst if x.species == entity_type]

        return visible
