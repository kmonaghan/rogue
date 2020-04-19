import tcod

class FOV:
    def __init__(self, fov_algorithm=tcod.FOV_RESTRICTIVE, fov_light_walls=True, fov_radius=10):
        self.fov_algorithm = fov_algorithm
        self.fov_light_walls = fov_light_walls
        self.fov_radius = fov_radius
