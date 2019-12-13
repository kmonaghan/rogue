from equipment_slots import EquipmentSlots

class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self):
        self.main_hand = None
        self.off_hand = None
        self.chest = None
        self.head = None
        self.left_ring_finger = None
        self.right_ring_finger = None

    @property
    def max_hp_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus

        if self.chest and self.chest.equippable:
            bonus += self.chest.equippable.max_hp_bonus

        if self.head and self.head.equippable:
            bonus += self.head.equippable.max_hp_bonus

        if self.left_ring_finger and self.left_ring_finger.equippable:
            bonus += self.left_ring_finger.equippable.max_hp_bonus

        if self.right_ring_finger and self.right_ring_finger.equippable:
            bonus += self.right_ring_finger.equippable.max_hp_bonus

        return bonus

    @property
    def power_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.power_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.power_bonus

        if self.chest and self.chest.equippable:
            bonus += self.chest.equippable.power_bonus

        if self.head and self.head.equippable:
            bonus += self.head.equippable.power_bonus

        if self.left_ring_finger and self.left_ring_finger.equippable:
            bonus += self.left_ring_finger.equippable.power_bonus

        if self.right_ring_finger and self.right_ring_finger.equippable:
            bonus += self.right_ring_finger.equippable.power_bonus

        return bonus

    @property
    def defence_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defence_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defence_bonus

        if self.chest and self.chest.equippable:
            bonus += self.chest.equippable.defence_bonus

        if self.head and self.head.equippable:
            bonus += self.head.equippable.defence_bonus

        if self.left_ring_finger and self.left_ring_finger.equippable:
            bonus += self.left_ring_finger.equippable.defence_bonus

        if self.right_ring_finger and self.right_ring_finger.equippable:
            bonus += self.right_ring_finger.equippable.defence_bonus

        return bonus

    def toggle_equip(self, equippable_entity):
        results = []

        slot = equippable_entity.equippable.slot
        equiped = False

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.main_hand:
                    results.append({'dequipped': self.main_hand})

                self.main_hand = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.off_hand:
                    results.append({'dequipped': self.off_hand})

                self.off_hand = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True
        elif slot == EquipmentSlots.CHEST:
            if self.chest == equippable_entity:
                self.chest = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.chest:
                    results.append({'dequipped': self.chest})

                self.chest = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True
        elif slot == EquipmentSlots.HEAD:
            if self.head == equippable_entity:
                self.head = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.head:
                    results.append({'dequipped': self.head})

                self.head = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True
        elif slot == EquipmentSlots.RING:
            if not self.left_ring_finger:
                self.left_ring_finger = equippable_entity
                results.append({'equipped': equippable_entity})
            elif not self.right_ring_finger:
                self.right_ring_finger = equippable_entity
                results.append({'equipped': equippable_entity})
            else:
                if self.left_ring_finger:
                    results.append({'dequipped': self.left_ring_finger})

                self.left_ring_finger = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True
        elif slot == EquipmentSlots.LEFT_RING_FINGER:
            if self.left_ring_finger == equippable_entity:
                self.left_ring_finger = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.left_ring_finger:
                    results.append({'dequipped': self.head})

                self.left_ring_finger = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True
        elif slot == EquipmentSlots.RIGHT_RING_FINGER:
            if self.right_ring_finger == equippable_entity:
                self.right_ring_finger = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.right_ring_finger:
                    results.append({'dequipped': self.head})

                self.right_ring_finger = equippable_entity
                results.append({'equipped': equippable_entity})
                equiped = True

        if equiped:
            equippable_entity.equippable.on_equip()
        else:
            equippable_entity.equippable.on_dequip()

        return results

    def get_equipped_in_slot(self, slot):  #returns the equipment in a slot, or None if it's empty
        if slot == EquipmentSlots.MAIN_HAND:
            return self.main_hand

        if slot == EquipmentSlots.OFF_HAND:
            return self.off_hand

        if slot == EquipmentSlots.CHEST:
            return self.chest

        if slot == EquipmentSlots.HEAD:
            return self.head

        if slot == EquipmentSlots.LEFT_RING_FINGER:
            return self.left_ring_finger

        if slot == EquipmentSlots.RIGHT_RING_FINGER:
            return self.right_ring_finger

        return None
