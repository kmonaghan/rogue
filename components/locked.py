class Locked:
    def __init__(self, locked = True, blocks_while_unlocked = False, requires_key = False):
        self.locked = locked
        self.blocks_while_unlocked = blocks_while_unlocked
        self.owner = None
        self.requires_key = requires_key

    def __str__(self):
        return f"Locked: {self.locked}"

    def toggle(self):
        self.locked = not self.locked

        if self.locked or self.blocks_while_unlocked:
            print("setting blocking")
            self.owner.blocks = True
        else:
            print("setting unblocked")
            self.owner.blocks = False
