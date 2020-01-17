class Energy:
    def __init__(self, act_energy = 1):
        self.current_energy = act_energy
        self.act_energy = act_energy
        self.owner = None

    @property
    def can_act(self):
        return (self.current_energy >= self.act_energy)

    def increase_energy(self, amount = 1):
        self.current_energy += amount
        print(f"{self.owner.name} energy: {self.current_energy} of {self.act_energy}")

    def take_action(self):
        if self.can_act:
            self.current_energy = 0
            return True
        else:
            return False
