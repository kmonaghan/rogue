import codecs

class Identifiable:
    #an item that can be picked up and used.
    def __init__(self):
        self.identified = False

    @property
    def name(self):
        return codecs.encode(self.owner.base_name, 'rot_13')
