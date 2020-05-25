class Display:
    #an item that can be picked up and used.
    def __init__(self, characters= []):
        self.characters = characters
        self.idx = 0

    @property
    def display_char(self):
        self.idx += 1
        if self.idx >= len(self.characters):
            self.idx = 0

        return self.characters[self.idx]
