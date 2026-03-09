from typing import Literal
from pydantic import BaseModel


# do not use elsewhere
AvailableSlotsGear = Literal["helmet", "chestplate", "leggings", "boots"]
AvailableSlotsAccessories = Literal["finger"]  # just this place for now
SlotWeaponLight = Literal["one-handed", "one-handed-and-shield", "shield"]  
SlotWeaponHeavy = Literal["two-handed"]


class Gear(BaseModel):
    """
    This stuff validates the data so that i dont have to care much
    Baseclass doesnt include slot because subclasses handle it
    """

    name: str
    hp_add: float
    speed_add: float = 0  # this is only for boots
    slot: AvailableSlotsGear
    drop_rate: float


class _Weapon(BaseModel):
    """
    Base class for weapons. Shouldn't be used directly
    """
    name: str
    slot: SlotWeaponLight | SlotWeaponHeavy
    drop_rate: float
    # TODO: replace not universally-used values


class WeaponOnly(_Weapon):
    slot: SlotWeaponLight = "one-handed"
    attack_add: float

class WeaponAndShield(_Weapon):
    slot: SlotWeaponLight = "one-handed-and-shield"
    attack_add: float
    hp_add: float

class ShieldOnly(_Weapon):
    slot: SlotWeaponLight = "shield"
    hp_add: float


class TwoHanded(_Weapon):
    slot: SlotWeaponHeavy = "two-handed"
    attack_add: float


class Accessory(BaseModel):
    name: str
    hp_multiply: float
    attack_multiply: float
    speed_multiply: float | None = None   # shouldn't be used universally
    slot: AvailableSlotsAccessories
    drop_rate: float