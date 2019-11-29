class Unlock:
    def __init__(self, unlocks):
        self.unlocks = unlocks
        self.owner = None

    def __str__(self):
        return f"Unlocks door: {self.unlocks}"
