from etc.enum import DamageType

class Resistance:
    def __init__(self, default = 1,
                        blunt = 1,
                        sharp = 1,
                        fire = 1,
                        ice = 1,
                        electric = 1):
        self.default = default
        self.blunt = blunt
        self.sharp = sharp
        self.fire = fire
        self.ice = ice
        self.electric = electric

    def modifier(self, type):
        if type == DamageType.DEFAULT:
            return self.default
        elif type == DamageType.BLUNT:
            return self.blunt
        elif type == DamageType.SHARP:
            return self.sharp
        elif type == DamageType.FIRE:
            return self.fire
        elif type == DamageType.ICE:
            return self.ice
        elif type == DamageType.ELECTRIC:
            return self.electric

        return 1;
