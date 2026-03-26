"""
Player cache service
Handles serialization/deserialization of GamePlayer to/from Redis
"""

import json
from uuid import UUID
from redis.asyncio import Redis

from game_internals.core.gameplay.entities.player import Player as GamePlayer
from game_internals.core.schemas.items import (
    Gear,
    Accessory,
    WeaponOnly,
    WeaponAndShield,
    ShieldOnly,
    TwoHanded,
)


def serialize_item(item) -> dict | None:
    """Serialize item with type information for reconstruction"""
    if item is None:
        return None

    item_dict = item.model_dump()
    item_dict["__type__"] = item.__class__.__name__
    return item_dict


def deserialize_item(item_dict: dict | None):
    """Deserialize item back to proper Pydantic model"""
    if item_dict is None:
        return None

    type_map = {
        "Gear": Gear,
        "Accessory": Accessory,
        "WeaponOnly": WeaponOnly,
        "WeaponAndShield": WeaponAndShield,
        "ShieldOnly": ShieldOnly,
        "TwoHanded": TwoHanded,
    }

    item_type = item_dict.pop("__type__", None)
    if not item_type or item_type not in type_map:
        return None

    return type_map[item_type](**item_dict)


def game_player_to_dict(player: GamePlayer) -> dict:
    """Serialize GamePlayer to dict for Redis storage"""
    return {
        "name": player.name,
        "base_hp": player.base_hp,
        "base_attack": player.base_attack,
        "base_speed": player.base_speed,
        "current_hp": player.current_hp,
        "current_attack": player.current_attack,
        "current_speed": player.current_speed,
        "coins": player.coins,
        "floor": player.floor,
        "best_run": player.best_run,
        "equipped": {
            slot: serialize_item(item)
            for slot, item in player.equipped.items()
        },
    }


def dict_to_game_player(data: dict) -> GamePlayer:
    """Deserialize dict from Redis to GamePlayer"""
    player = GamePlayer(
        name=data["name"],
        hp=data["base_hp"],
        attack=data["base_attack"],
        speed=data["base_speed"],
    )
    player.current_hp = data["current_hp"]
    player.current_attack = data["current_attack"]
    player.current_speed = data["current_speed"]
    player.coins = data["coins"]
    player.floor = data["floor"]
    player.best_run = data.get("best_run")

    # Reconstruct equipment
    for slot, item_dict in data["equipped"].items():
        player.equipped[slot] = deserialize_item(item_dict)

    return player


async def get_cached_player(player_id: UUID, redis: Redis) -> GamePlayer | None:
    """Get player from Redis cache"""
    cache_key = f"game_session:{player_id}"
    cached = await redis.get(cache_key)

    if not cached:
        return None

    data = json.loads(cached)
    return dict_to_game_player(data)


async def cache_player(player_id: UUID, game_player: GamePlayer, redis: Redis, ttl: int = 7200):
    """Store player in Redis cache with TTL (default 2 hours)"""
    cache_key = f"game_session:{player_id}"
    data = game_player_to_dict(game_player)
    await redis.set(cache_key, json.dumps(data), ex=ttl)


async def clear_cached_player(player_id: UUID, redis: Redis):
    """Remove player from Redis cache"""
    cache_key = f"game_session:{player_id}"
    await redis.delete(cache_key)
