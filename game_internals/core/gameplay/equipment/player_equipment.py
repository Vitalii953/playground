from __future__ import annotations
import logging
from typing import Optional


log = logging.getLogger(__name__)


def _validate_slot(player: Player, slot: str) -> None:  # type: ignore
    from game.gameplay.entities.player import Player
    from game.gameplay.equipment.errors import EquipmentError
    from game.gameplay.equipment.items.item import Item

    if slot not in player.equipment:
        log.warning(f"{player.name} couldn't equip an item to invalid slot: {slot}")
        raise EquipmentError(f"Invalid equipment slot: {slot}")


def _validate_item_available(player: "Player", item: Item) -> None:  # type: ignore
    from game.gameplay.equipment.items.item import Item
    from game.gameplay.equipment.errors import EquipmentError

    if not isinstance(item, Item):
        raise TypeError("item must be an Item instance")
    if player.inventory.get(item, 0) < 1:
        log.warning(
            f"{player.name} couldn't equip {item.name} as it wasn't in their inventory"
        )
        raise EquipmentError(f"Item {item.name} not in inventory")


def _validate_slot_compatibility(slot: str, item: Item) -> None:  # type: ignore
    from game.gameplay.equipment.items.item import Item
    from game.gameplay.equipment.errors import EquipmentError

    if item.slot != slot:
        log.warning(f"{item.name} can't be equipped into {item.slot}")
        raise EquipmentError(f"Item {item.name} cannot be equipped into {slot}")


def _apply_from_equipment(player: "Player") -> None:  # type: ignore
    from game.gameplay.entities.player import Player

    # temporary in this function
    total_attack = player.base_attack
    total_hp = player.base_hp
    total_speed = player.base_speed

    for item in player.equipment.values():
        if item is None:
            continue
        total_attack = total_attack * item.attack_multiply + item.attack_add
        total_hp = total_hp * item.hp_multiply + item.hp_add
        total_speed = total_speed + item.speed
    # safeguards
    player.attack = max(0, total_attack)
    player.hp = max(1, total_hp)
    player.speed = max(1, total_speed)


def equip_item(player: "Player", slot: str, item: Item) -> dict:  # type: ignore
    from game.gameplay.entities.player import Player
    from game.gameplay.equipment.items.item import Item

    _validate_slot(player, slot)
    _validate_item_available(player, item)
    _validate_slot_compatibility(slot, item)

    old_item = player.equipment.get(slot)
    if old_item:
        player.add_item(old_item, 1)

    player.remove_item(item, 1)
    player.equipment[slot] = item
    _apply_from_equipment(player)
    log.info(f"{player.name} equipped {item.name} to {slot}")

    return {
        "status": "equipped",
        "slot": slot,
        "equipped": item.name,
        "replaced": getattr(old_item, "name", None),
    }
