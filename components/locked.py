class Locked:
    def __init__(self, locked = True, blocks_while_unlocked = False, requires_key = False, locked_character=None, unlocked_character=None):
        self.locked = locked
        self.blocks_while_unlocked = blocks_while_unlocked
        self.owner = None
        self.requires_key = requires_key
        self.locked_character = locked_character
        self.unlocked_character = unlocked_character

    def __str__(self):
        return f"Locked: {self.locked}"

    def toggle(self):
        self.locked = not self.locked

        if self.locked or self.blocks_while_unlocked:
            self.owner.blocks = True
            if self.locked_character:
                self.owner.char = self.locked_character
        else:
            self.owner.blocks = False
            self.owner.transparent = True

            if self.unlocked_character:
                self.owner.char = self.unlocked_character
