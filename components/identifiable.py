import codecs

class Identifiable:
    #an item that can be picked up and used.
    def __init__(self):
        self.identified = False
        self.common_ident = False
        self.chance_to_identify = 90
        self.identified_on_use_message = ''
        self.owner = None
    @property
    def name(self):
        return codecs.encode(self.owner.base_name, 'rot_13')

class IdentifiableWeapon(Identifiable):
    def __init__(self, base_name=None):
        super().__init__()
        self.base_name = base_name
        self.identified_on_use_message = f"Power surges through {self.base_name} and reveals true self."

    @property
    def name(self):
        return f'an excellent quality {self.base_name}'

class IdentifiableScroll(Identifiable):
    def __init__(self):
        super().__init__()
        self.common_ident = True

    @property
    def name(self):
        return f'A scroll titled "{codecs.encode(self.owner.base_name, "rot_13")}"'

class IdentifiablePotion(Identifiable):
    def __init__(self, container='jar', liquid_color='red', liquid_type='viscous'):
        super().__init__()
        self.container = container
        self.liquid_color = liquid_color
        self.liquid_type = liquid_type
        self.common_ident = True

    @property
    def name(self):
        return f'A {self.container} containing a {self.liquid_color}, {self.liquid_type} liquid'
