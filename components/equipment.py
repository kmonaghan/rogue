from etc.enum import EquipmentSlot, string_to_equipment_slot

class Equipment:
    '''
    An object that manages all the items that an enity has equipped.

    Attributes
    ----------
    equipped : dictionary
        Stores all the equipped items.
    '''
    def __init__(self):
        self.equipped = {}
        for value in string_to_equipment_slot.values():
            self.equipped[value] = None

    @property
    def defence(self):
        """Return the total defence bonus from all equipped items."""
        bonus = 0

        for item in self.equipped.values():
            if item:
                bonus += item.equippable.defence

        return bonus

    @property
    def max_hp_bonus(self):
        """Return the hit point bonus from all equipped items."""
        bonus = 0
        for item in self.equipped.values():
            if item:
                bonus += item.equippable.max_hp_bonus

        return bonus

    @property
    def power(self):
        """Return the total power bonus from all equipped items."""
        bonus = 0

        for item in self.equipped.values():
            if item:
                bonus += item.equippable.power

        return bonus

    def toggle_equip(self, equippable_entity):
        '''Attempt to equip an item.

        If an item is already equipped in the appropriate slot, the current item
        will be depuipped first and then the new item equipped.

        Rings are handled seperately.

        Parameters
        ----------
        equippable_entity : Entity
            The item to attempt to equip.

        Returns
        -------
        results
            An array with the processed results.
        '''
        results = []

        slot = equippable_entity.equippable.slot

        equipped = None
        dequipped = None

        if (slot == EquipmentSlot.RING
            or slot == EquipmentSlot.LEFT_RING_FINGER
            or slot == EquipmentSlot.RIGHT_RING_FINGER):
            results.extend(self.toggle_equip_ring(equippable_entity))
            return results
        else:
            if self.equipped[slot] == equippable_entity:
                self.equipped[slot] = None
                results.append({'dequipped': equippable_entity})
                dequipped = equippable_entity
            else:
                if self.equipped[slot]:
                    results.append({'dequipped': self.equipped[slot]})
                    dequipped = equippable_entity
                if self.equipped[slot] != equippable_entity:
                    self.equipped[slot] = equippable_entity
                    results.append({'equipped': equippable_entity})
                    equipped = equippable_entity

        if equipped:
            equipped.equippable.on_equip(self.owner)

        if dequipped:
            dequipped.equippable.on_dequip(self.owner)

        return results

    def toggle_equip_ring(self, equippable_entity):
        '''Attempt to equip a ring.
        If the entity has no rings equipped, the ring is equipped on the left
        hand.
        If the entity has a ring on the left hand, the ring is equipped on the
        right hand.
        If the entity has a ring on both hands, the current ring on the left
        hand is dequipped and the

        Parameters
        ----------
        equippable_entity : Entity
            The ring to attempt to equip.

        Returns
        -------
        results
            An array with the processed results.
        '''
        results = []

        equipped = None
        dequipped = None

        if self.equipped[EquipmentSlot.LEFT_RING_FINGER] == equippable_entity:
            dequipped = self.equipped[EquipmentSlot.LEFT_RING_FINGER]
            self.equipped[EquipmentSlot.LEFT_RING_FINGER] = None
            results.append({'dequipped': equippable_entity})
        elif self.equipped[EquipmentSlot.RIGHT_RING_FINGER] == equippable_entity:
            dequipped = self.equipped[EquipmentSlot.RIGHT_RING_FINGER]
            self.equipped[EquipmentSlot.RIGHT_RING_FINGER] = None
            results.append({'dequipped': equippable_entity})
        else:
            if not self.equipped[EquipmentSlot.LEFT_RING_FINGER]:
                self.equipped[EquipmentSlot.LEFT_RING_FINGER] = equippable_entity
                results.append({'equipped': equippable_entity})
                equipped = equippable_entity
            elif not self.equipped[EquipmentSlot.RIGHT_RING_FINGER]:
                self.equipped[EquipmentSlot.RIGHT_RING_FINGER] = equippable_entity
                results.append({'equipped': equippable_entity})
                equipped = equippable_entity
            else:
                dequipped = self.equipped[EquipmentSlot.LEFT_RING_FINGER]
                results.append({'dequipped': self.equipped[EquipmentSlot.LEFT_RING_FINGER]})
                results.append({'equipped': equippable_entity})
                equipped = equippable_entity

        if equipped:
            equipped.equippable.on_equip(self.owner)

        if dequipped:
            dequipped.equippable.on_dequip(self.owner)

        return results

    def get_equipped_in_slot(self, slot):
        '''Return the item (if any) equipped in a particular slot.

        Parameters
        ----------
        slot : EquipmentSlot
            The slot to be checked for an item.

        Returns
        -------
        Entity or None
            Item that is equipped in slot.
        '''
        return self.equipped.get(slot)
