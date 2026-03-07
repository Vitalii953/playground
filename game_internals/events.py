from __future__ import annotations
from random import randint, uniform, random, choice, choices
from typing import Optional


# lucky
def heal_event(player: Player):  # type: ignore
    from game.gameplay.entities.player import Player

    _amount = randint(1, 35)
    player.heal(_amount)
    return {"type": "heal", "value": _amount}


def random_item_event(player: Player):  # type: ignore
    from game.gameplay.entities.player import Player
    from game.gameplay.equipment.items.item import Item
    from game.gameplay.equipment.items.items_list import (
        SWORDS,
        HELMETS,
        CHESTS,
        BOOTS,
        WINGS,
        ALL_ITEMS,
        CATEGORY_CHANCES,
    )

    # decide item type based on CATEGORY_CHANCES
    _types = list(CATEGORY_CHANCES.keys())
    _chances = list(CATEGORY_CHANCES.values())
    # respects _chances
    _select_type = choices(_types, weights=_chances, k=1)[0]
    _chosen_item = choice(list(ALL_ITEMS[_select_type].values()))
    # need to map because values ≠ keys in player.equipment
    _MAPPING = {
        "swords": "weapon",
        "helmets": "helmet",
        "chests": "chest",
        "boots": "boots",
        "wings": "wings",
    }

    slot = _MAPPING[_select_type]
    if player.equipment[slot] is None:
        player.add_item(_chosen_item)
        player.equip(slot, _chosen_item)
    else:
        player.add_item(_chosen_item)

    return {"type": "random item", "value": _chosen_item.name}


def floor_up_event(player: Player):  # type: ignore
    from game.gameplay.entities.player import Player

    _amount = 1
    if random() < 0.1:
        _amount = 2
    player.floor += _amount
    return {"type": "floor_up", "value": _amount}


def add_coins_event(player: Player):  # type: ignore
    from game.gameplay.entities.player import Player

    _amount = randint(10, 30)
    if random() < 0.5:
        _amount = randint(30, 40)
    if random() < 0.1:
        _amount = randint(40, 50)
    player.coins += _amount
    return {"type": "add coins", "value": _amount}


# unlucky


def summon_enemy_event(player: Player, enemy: Optional[str] = None):  # type: ignore
    from game.gameplay.entities.enemies import reinforce_enemy
    from game.gameplay.entities.player import Player
    from game.gameplay.entities.enemies_list import HUMANOIDS, MONSTERS
    from game.gameplay.combat_logic.adventure import fight_to_death

    all_enemies = {**HUMANOIDS, **MONSTERS}

    # now utilizes factory pattern
    if not enemy:
        enemy = choice(list(all_enemies.keys()))
    if enemy not in all_enemies:
        raise ValueError(
            f"Provided enemy ({enemy}) can't be initialized as it's invalid"
        )

    opponent = all_enemies[enemy]()
    opponent = reinforce_enemy(opponent, player.floor)

    res = fight_to_death(player, opponent)
    return {"type": "enemy", "value": opponent.name, "report": res}


def poison_event(player: Player):  # type: ignore
    from game.gameplay.entities.player import Player

    damage = randint(10, 30)
    player.hp -= damage

    return {"type": "poison", "value": damage}


def floor_down_event(player: Player):  # type: ignore
    from game.gameplay.entities.player import Player

    _amount = 1
    if random() < 0.1:
        _amount = 2
    player.floor = max(0, player.floor - _amount)
    return {"type": "floor_down", "value": _amount}
