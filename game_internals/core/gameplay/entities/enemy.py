from game_internals.core.gameplay.entities.entity import Entity
from random import uniform


class Enemy(Entity):
    def __init__(
        self,
        name: str,
        hp: int | float,
        attack: int | float,
        speed: int | float,
        coins_loot: int = 0,
    ):
        super().__init__(name=name, hp=hp, attack=attack, speed=speed)

        self.coins_loot = coins_loot

    def is_alive(self) -> bool:
        return self.base_hp > 0

    def heal_by(self, value: int | float) -> int | float:
        self.base_hp += value
        return self.base_hp

    def attack_(self, target: Entity) -> int | float:
        multiplier = uniform(0.6, 1.5)
        crit: bool = multiplier >= 1.2
        dmg = min(round(self.base_attack * multiplier, 2), 50)  # 50 attack is max
        if crit:
            dmg += self.base_attack * 0.2

        target.current_hp -= min(dmg, target.base_hp)

        return dmg

    def die(self) -> int:
        """
        can't pass player as argument and add coins - severe SoC violation
        """
        return self.coins_loot
