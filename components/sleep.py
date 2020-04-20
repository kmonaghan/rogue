from components.fov import FOV

class Sleep:
    def __init__(self):
        self.old_fov = None

    def start(self):
        self.old_fov = self.owner.fov
        self.owner.del_component('fov')
        self.owner.add_component(FOV(fov_radius=1), 'fov')

    def on_turn(self, game_map):
        self.owner.health.heal(2)

        if self.owner.health.max_hp == self.owner.health.hp:
            self.end()
            return True

        return False

    def end(self):
        if self.owner:
            self.owner.del_component('fov')
            self.owner.add_component(self.old_fov, 'fov')
            self.owner.del_component('sleep')
        else:
            print('no owner?')
