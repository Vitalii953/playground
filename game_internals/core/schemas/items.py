from typing import Literal
from pydantic import BaseModel


AvailableSlotsGear = Literal["helmet", "chestplate", "leggings", "boots"]
AvailableSlotsAccessories = Literal["finger"]  # just this place for now
SlotWeaponLight = Literal["one-handed", "shield"]
SlotWeaponHeavy = Literal["two-handed"]


class Gear(BaseModel):
    """
    This stuff validates the data so that i dont have to care much
    Baseclass doesnt include slot because subclasses handle it
    """
    name: str
    hp_add: float
    speed_add: float = 0 # this is only for boots, maybe accessories too
    slot: AvailableSlotsGear

class Weapon(BaseModel):
    name: str
    attack_add: float
    slot: SlotWeaponLight | SlotWeaponHeavy

class Accessory(BaseModel):
    name: str
    hp_multiply: float
    attack_multiply: float
    slot: AvailableSlotsAccessories

    


    