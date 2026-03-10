from __future__ import annotations
from random import uniform


class Entity:
    def __init__(
        self,
        name: str,
        hp: int | float,
        attack: int | float,
        speed: int | float,
    ):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.speed = speed

    def is_alive(self) -> bool:
        return self.hp > 0

    
    def take_damage(self, damage: int | float) -> int | float:
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return self.hp

    def heal_by(self, value: int | float) -> int | float:
        self.hp += value
        return self.hp


    def attack_target(self, target: Entity) -> int | float:
        multiplier = uniform(0.6, 1.5)
        crit: bool = multiplier >= 1.2
        dmg = min(round(self.attack * multiplier, 2), 50)  # 50 attack is max
        if crit:
            dmg += self.attack * 0.2

        target.take_damage(dmg)
        return dmg
        