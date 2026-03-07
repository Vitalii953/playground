from __future__ import annotations
from game.gameplay.entities.entities import Entity  # circular import not possible here

import time
import logging
from typing import Optional


log = logging.getLogger(__name__)


class Player(Entity):  # type: ignore

    def __init__(
        self, name: str, hp: int | float, attack: int | float, speed: int | float
    ):
        from game.gameplay.entities.entities import Entity
        from game.gameplay.equipment.items.item import Item

        super().__init__(name=name, hp=hp, attack=attack, speed=speed)
        self.base_hp = self.hp
        self.base_attack = self.attack
        self.base_speed = self.speed

        self.inventory: dict[Item, int] = {}
        self.equipment: dict[str, Item | None] = {
            "weapon": None,
            "helmet": None,
            "chest": None,
            "boots": None,
            "wings": None,
        }

        # flags added if suspended (triggered by logs)
        self.flags = 0
        # coins will be used to buy items that give lifetime buffs
        self.coins = 0
        self.floor = 0
        self.start_time: Optional[float] = None
        self.best_run: Optional[tuple[int, float | None]] = None

        log.info(
            f"{self.name} has been created with the following stats:\n{self.hp}\n{self.attack}\n{self.speed}\nEquipment: {self.equipment}"
        )

        # ====== EQUIPMENT =======

    def add_item(self, item: Item, quantity: int = 1) -> None:  # type: ignore
        from game.gameplay.equipment.items.item import Item

        if not isinstance(item, Item):
            self.flags += 1
            log.warning(
                f"{self.name} attempted to add {item} which is invalid. Flagged"
            )
            raise TypeError(f"Invalid type ({item}) wasn't added to the inventory")
        self.inventory[item] = self.inventory.get(item, 0) + quantity
        log.info(f"{self.name} put {quantity} of {item.name} in their inventory")

    def remove_item(self, item: Item, quantity: int = 1) -> None:  # type: ignore
        from game.gameplay.equipment.errors import EquipmentError
        from game.gameplay.equipment.items.item import Item

        if not isinstance(item, Item):
            self.flags += 1
            log.warning(
                f"{self.name} attempted to remove {item} which is invalid. Flagged"
            )
            raise TypeError(f"Invalid type ({item}) wasn't removed from the inventory")
        current = self.inventory.get(item, 0)
        if quantity > current:
            self.flags += 1
            log.warning(
                f"{self.name} attempted to remove {item.name} in quantity of {quantity}. Flagged"
            )
            raise EquipmentError(
                f"Not enough {item.name} to remove. You currently have {current} of {item.name}, {quantity} requested."
            )

        new_quantity = current - quantity
        if new_quantity == 0:
            del self.inventory[item]
            log.info(
                f"{item.name} deleted from {self.name}'s inventory because quantity reached 0"
            )
        else:
            self.inventory[item] = new_quantity
            log.info(
                f"{self.name}'s new quantity of {item.name} has diminished. Now {new_quantity}"
            )

    def equip(self, slot: str, item: Item):  # type: ignore
        from game.gameplay.equipment.items.item import Item
        from game.gameplay.equipment.player_equipment import equip_item

        # best option is to return it as equip_item contains returns too
        equipped = equip_item(self, slot, item)
        log.info(f"{self.name} equipped {item.name} to {slot}")
        return equipped

    # ====== TIMER, FLOOR =======

    def start_timer(self):
        if self.floor == 0:
            self.start_time = time.time()
            log.info(f"time started for {self.name}")

    def end_timer(self):
        # edge case
        if self.start_time is None:
            self.flags += 1
            log.warning(
                f"{self.name} tried to end the timer without starting it. Flagged"
            )
            raise ValueError("end timer error: start is None")

        end = time.time()
        duration = end - self.start_time

        # first run ever
        if self.best_run is None:
            self.best_run = (self.floor, duration)
            log.info(
                f"{self.name} has made their first run ever.\nFloor: {self.floor}\nDuration: {duration}"
            )
            return

        # higher floor
        if self.best_run[0] < self.floor:
            self.best_run = (self.floor, duration)
            log.info(
                f"{self.name} has made it to a higher floor.\nFloor: {self.floor}\nDuration: {duration}"
            )
            return

        # same floor but quicker
        if self.best_run[0] == self.floor and self.best_run[1] > duration:
            self.best_run = (self.floor, duration)
            log.info(
                f"{self.name} has made a new record on the same floor.\nFloor: {self.floor}\nDuration: {duration}"
            )
            return

    def pass_floor(self):
        self.floor += 1
        log.info(f"1 floor passed for {self.name}")

    def end_run(self):
        # end timer, reset floor, reset self.start_time
        if self.start_time is None:
            self.flags += 1
            log.warning(
                f"{self.name} tried to end run without starting a timer. Flagged"
            )
            raise ValueError("end run error: start is None")

        self.end_timer()
        self.floor = 0
        self.start_time = None
