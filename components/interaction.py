from etc.enum import Interactions

class Interaction:
    def __init__(self, interaction_type = Interactions.FOE):
        self.interaction_type = interaction_type
        self.owner = None

    def __str__(self):
        return f"Interaction type: {self.interaction_type}"
