from __future__ import annotations
from random import uniform
import logging
from game.config.loader import load_config

log = logging.getLogger(__name__)


class Entity:
    def __init__(
        self,
        name: str,
        hp: int | float = 100,
        attack: int | float = 10,
        speed: int | float = 10,
    ):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.speed = speed

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int | float) -> None:
        self.hp = max(0, (self.hp - damage))

    def heal(self, value: int | float) -> None:
        # Cap healing at base_hp if available, otherwise no cap
        if hasattr(self, "base_hp"):
            self.hp = min(self.hp + value, self.base_hp)
        else:
            self.hp += value

    def attack_target(self, target: Entity) -> dict:  # type: ignore
        from game.gameplay.entities.entities import Entity

        if not isinstance(target, Entity):
            log.error(f"{self.name} tried to attack {target}")
            raise TypeError("This is not an entity that you try to attack")

        multiplier = uniform(0.6, 1.5)
        crit = multiplier >= 1.2
        dmg = min(round(self.attack * multiplier, 2), 50)  # 50 attack is max
        target.take_damage(dmg)
        crit_txt = " (CRIT DMG)" if crit else ""
        log.info(
            f"{self.name} attacked {target.name} and dealt {dmg} damage{crit_txt}. Target now has {target.hp} HP"
        )
        return {
            "attacker": self.name,
            "target": target.name,
            "damage": dmg,
            "crit": crit,
            "target_hp": target.hp,
        }
