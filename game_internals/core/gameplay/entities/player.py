from __future__ import annotations
from random import uniform
from game_internals.core.gameplay.entities.entity import Entity  
from game_internals.core.schemas.items import Accessory, Gear, ShieldOnly, TwoHanded, WeaponAndShield, WeaponOnly, _Weapon

"""
IMPORTANT: stats MUST be read at the start of each turn to:
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

        self.current_hp = self.total_hp   # smart thing - calls properties 
        self.current_attack = self.total_attack  # for runtime and dynamic buffs
        self.current_speed = self.total_speed



    @property
    # reminder: properties are read-only
    def total_hp(self) -> int | float:
        """
        only access hp via this API
        """
        hp = self.base_hp
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

        """
        only access attack via this API
        """

        atk = self.base_attack
        for item in self.equipped.values():
            # we can extract attributes
            if item is not None and hasattr(item, "attack_add"):
                atk += getattr(item, "attack_add")  # gettatr to shut up IDE

        # this must run after because multipliers multiply overall hp
        for item in self.equipped.values():
            if item is not None and hasattr(item, "attack_multiply"):
                atk *= getattr(item, "attack_multiply")

        return atk


    @property
    def total_speed(self) -> int | float:

        """
        only access speed via this API
        """

        spd = self.base_speed
        for item in self.equipped.values():
            # we can extract attributes
            if item is not None and hasattr(item, "speed_add"):
                spd += getattr(item, "speed_add")  # gettatr to shut up IDE

        for item in self.equipped.values():
            if item is not None and hasattr(item, "speed_multiply"):
                spd *= getattr(item, "speed_multiply")

        return spd
        

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
        # sync current stats
        self.current_hp = self.total_hp
        self.current_attack = self.total_attack
        self.current_speed = self.total_speed
        return True
    

    def mount_floor(self, value: int = 1):
        self.floor += value
        return self.floor


    def add_coins(self, value: int):
        self.coins += value
        return self.coins


    def eval_runtime(self, run_time: int | float):
        """
        should be called at the end of every run, not just the best one
        """
        if self.best_run is None or run_time < self.best_run:
            self.best_run = run_time
        return self.best_run
    
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def heal_by(self, value: int | float) -> int | float:
        self.current_hp = min(self.current_hp + value, self.base_hp)
        return self.current_hp


    def attack_(self, target: Entity) -> int | float:
        multiplier = uniform(0.6, 1.5)
        crit: bool = multiplier >= 1.2
        dmg = min(round(self.current_attack * multiplier, 2), 50)  # 50 attack is max
        if crit:
            dmg += self.base_attack * 0.2
        target.base_hp -= min(dmg, target.base_hp)

        return dmg


    def die(self, run_time: int | float):
        self.eval_runtime(run_time)
        self.floor = 0