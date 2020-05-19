from etc.enum import DamageType

class DamageModifier:
    '''
    The DamageModifier object contains a list of modifiers to be used when
    determing the actual damage caused to an entity.

    The modifier is expressed as a float.

    Therefore, an entity recieving 10 damage of DamageType.BLUNT that has a

    Parameters
    ----------
    default: float
        Modifier for DamageType.DEFAULT. Defaults to 100% damage.
    blunt: float
        Modifier for DamageType.BLUNT. Defaults to 100% damage.
    slashing: float
        Modifier for DamageType.SLASHING. Defaults to 100% damage.
    fire: float
        Modifier for DamageType.FIRE. Defaults to 100% damage.
    ice: float
        Modifier for DamageType.ICE. Defaults to 100% damage.
    electric: float
        Modifier for DamageType.ELECTRIC. Defaults to 100% damage.

    Attributes
    ----------
    default : float
        Stores base modifier for DamageType.DEFAULT.
    blunt : float
        Stores base modifier for DamageType.BLUNT.
    slashing : float
        Stores base modifier for DamageType.SLASHING.
    fire : float
        Stores base modifier for DamageType.FIRE.
    ice : float
        Stores base modifier for DamageType.ICE.
    electric : float
        Stores base modifier for DamageType.ELECTRIC.
    poison : float
        Stores base modifier for DamageType.POISON.
    '''
    def __init__(self, default = 1,
                        blunt = 1,
                        slashing = 1,
                        fire = 1,
                        ice = 1,
                        electric = 1,
                        poison = 1):
        self._default = default
        self._blunt = blunt
        self._slashing = slashing
        self._fire = fire
        self._ice = ice
        self._electric = electric
        self._poison = poison

    @property
    def default(self):
        """Return the fully calculated default damage modifier."""
        return self._default

    @property
    def blunt(self):
        """Return the fully calculated blunt damage modifier."""
        return self._blunt

    @property
    def slashing(self):
        """Return the fully calculated slashing damage modifier."""
        return self._slashing

    @property
    def fire(self):
        """Return the fully calculated fire damage modifier."""
        return self._fire

    @property
    def ice(self):
        """Return the fully calculated ice damage modifier."""
        return self._ice

    @property
    def electric(self):
        """Return the fully calculated electric damage modifier."""
        return self._electric

    @property
    def poison(self):
        """Return the fully calculated poison damage modifier."""
        return self._poison

    def modifier(self, type):
        '''Return the appropriate damage modifier for a given DamageType.
        If the DamageType is unknown, then the default modifier is returned.

        Parameters
        ----------
        type : DamageType
            The type of damage being caused.

        Returns
        -------
        float
            Damage modifier.
        '''
        if type == DamageType.BLUNT:
            return self.blunt
        elif type == DamageType.SLASHING:
            return self.slashing
        elif type == DamageType.FIRE:
            return self.fire
        elif type == DamageType.ICE:
            return self.ice
        elif type == DamageType.ELECTRIC:
            return self.electric
        elif type == DamageType.POISON:
            return self.poison

        #else type == DamageType.DEFAULT:
        return self.default
