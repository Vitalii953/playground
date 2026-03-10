from __future__ import annotations
from abc import ABC, abstractmethod


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
        self.current_hp = hp  # both enemy and player need it (change later if needed)
        self.base_attack = attack
        self.base_speed = speed

    @abstractmethod
    def is_alive(self) -> None: ...

    @abstractmethod
    def heal_by(self) -> None: ...

    @abstractmethod
    def attack_(self) -> None: ...

    @abstractmethod
    def die(self) -> None: ...
