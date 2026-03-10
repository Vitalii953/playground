from __future__ import annotations
from game_internals.core.gameplay.entities.entities import Entity  
from game_internals.core.schemas.items import Accessory, Gear, ShieldOnly, TwoHanded, WeaponAndShield, WeaponOnly, _Weapon

"""
IMPORTANT: stats MUST be read at the start of each turn to determine to:
see if player is alive; update buffs from equipment
"""

class Player(Entity):  

    def __init__(
        self, name: str, hp: int | float, attack: int | float, speed: int | float
    ):

        super().__init__(name=name, hp=hp, attack=attack, speed=speed)

        self.equipped: dict[
            str,
            Gear
            | WeaponOnly
            | WeaponAndShield
            | ShieldOnly
            | TwoHanded
            | Accessory
            | None,
        ] = {
            "one-handed": None,            # weapon
            "one-handed-and-shield": None,  # weapon
            "two-handed": None,     # weapon
            "shield": None,     # weapon too
            "helmet": None,
            "chestplate": None,
            "leggings": None,
            "boots": None,
            "finger": None,
        }

        self.coins = 0  # coins will be used to buy stuff
        self.floor = 0
        self.best_run: int | float | None = None  # i measure in seconds


    @property
    # reminder: properties are read-only
    def total_hp(self) -> int | float:
        """
        only access hp via this API
        """
        hp = self.hp
        for item in self.equipped.values():
            # we can extract attributes
            if item is not None and hasattr(item, "hp_add"):
                hp += getattr(item, "hp_add")  # gettatr to shut up IDE

        # this must run after because multipliers multiply overall hp
        for item in self.equipped.values(): 
            if item is not None and hasattr(item, "hp_multiply"):
                hp *= getattr(item, "hp_multiply")

        return hp
    

    @property
    def total_attack(self) -> int | float:
        # this reads all items at runtime and applies buffs
        """
        only access attack via this API
        """
        hp = self.hp
        for item in self.equipped.values():
            # we can extract attributes
            if item is not None and hasattr(item, "attack_add"):
                hp += getattr(item, "attack_add")  # gettatr to shut up IDE

        # this must run after because multipliers multiply overall hp
        for item in self.equipped.values():
            if item is not None and hasattr(item, "attack_multiply"):
                hp *= getattr(item, "attack_multiply")

        return hp


    @property
    def total_speed(self) -> int | float:
        # this reads all items at runtime and applies buffs
        """
        only access speed via this API
        """
        hp = self.hp
        for item in self.equipped.values():
            # we can extract attributes
            if item is not None and hasattr(item, "speed_add"):
                hp += getattr(item, "speed_add")  # gettatr to shut up IDE

        # this must run after because multipliers multiply overall hp
        for item in self.equipped.values():
            if item is not None and hasattr(item, "speed_multiply"):
                hp *= getattr(item, "speed_multiply")

        return hp
        

    def equip(self, item: Gear | WeaponOnly | WeaponAndShield | ShieldOnly | TwoHanded | Accessory) -> bool:
        """
        all equipment should be equipped via this method
        prevents multiple types of Weapon from being equipped all at once
        """
        # handle weapons
        if isinstance(item, _Weapon):
            for slot in self.equipped: 
                if slot in ("one-handed", "one-handed-and-shield", "two-handed", "shield"):
                    self.equipped[slot] = None
        self.equipped[item.slot] = item
        return True
    

    def mount_floor(self, value: int = 1):
        self.floor += value
        return self.floor


    def add_coins(self, value: int):
        self.coins += value
        return self.coins


    def finish_run(self, run_time: int | float):
        """
        should be called at the end of every run, not just the best one
        """
        if self.best_run is None or run_time < self.best_run:
            self.best_run = run_time
        return self.best_run
    

    