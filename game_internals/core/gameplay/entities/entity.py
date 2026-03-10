from __future__ import annotations
from abc import ABC, abstractmethod
from random import uniform


class Entity(ABC):
    def __init__(
        self,
        name: str,
        hp: int | float,
        attack: int | float,
        speed: int | float,
    ):
        self.name = name
        self.base_hp = hp
        self.current_hp = hp
        self.base_attack = attack
        self.current_attack = attack
        self.base_speed = speed
        self.current_speed = speed


    def is_alive(self) -> bool:
        return self.current_hp > 0


    def heal_by(self, value: int | float) -> int | float:
        self.current_hp += value
        return self.current_hp


    def attack_(self, target: Entity) -> int | float:
        multiplier = uniform(0.6, 1.5)
        crit: bool = multiplier >= 1.2
        dmg = min(round(self.current_attack * multiplier, 2), 50)  # 50 attack is max
        if crit:
            dmg += self.base_attack * 0.2
        target.current_hp -= min(dmg, target.current_hp)
        
        return dmg
        
    
    @abstractmethod
    def die(self) -> None:
        ...