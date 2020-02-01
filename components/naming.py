class Naming:
    def __init__(self, base_name, prefix = None, suffix = None):
        self.prefix = prefix
        self.base_name = base_name
        self.suffix = suffix

    @property
    def fullname(self):
        name = self.base_name
        if self.prefix:
            name = self.prefix + " " + name
        if self.suffix:
            name = name + " " + self.suffix

        return name
