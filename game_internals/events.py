from redis.asyncio import Redis
from backend.services.translator.translation_service import translate
from game_internals.core.gameplay.entities.player import Player
from game_internals.core.gameplay.entities.enemy import Enemy
from game_internals.core.gameplay.equipment.items_operations import pick_random_item
from game_internals.core.phrases import PHRASES
from game_internals.core.schemas.game_settings import languages
from random import randint


async def offer_random_item_event(language: languages, redis: Redis) -> dict:
    """
    This DOESN'T equip it immidiately, it just offers it to the player,
    frontend gives a choice to accept or not, and then other function processes it
    (2 functions and frontend to make it work)
    """

    item = pick_random_item()

    template = PHRASES["events"]["random_item"]
    formatted = template.format(item_name=item.name)
    result = await translate(formatted, language, redis)  # handles english too

    return {
        "language": language,
        "type": "random_item",
        "value": item.model_dump(),
        "report": result,
        "needs_input": True,
    }


async def floor_up_event(player: Player, language: languages, redis: Redis) -> dict:
    """
    Move the player up one floor
    """

    player.mount_floor(1)

    template = PHRASES["events"]["floor_up"]
    result = await translate(template, language, redis)  

    return {"language": language, "type": "floor_up", "report": result}


async def add_coins_event(player: Player, language: languages, redis: Redis) -> dict:
    """
    Gives some coins
    """

    coin_amount = randint(1, 20)
    player.add_coins(coin_amount)

    template = PHRASES["events"]["add_coins"]
    formatted = template.format(amount=coin_amount)
    result = await translate(formatted, language, redis)

    return {"language": language, "type": "add_coins", "value": coin_amount, "report": result}


async def floor_down_event(player: Player, language: languages, redis: Redis) -> dict:
    """
    Move the player down
    """

    player.descend_floor(1)

    template = PHRASES["events"]["floor_down"]
    result = await translate(template, language, redis)

    return {"language": language, "type": "floor_down", "report": result}


async def heal_event(player: Player, language: languages, redis: Redis) -> dict:
    """
    Player receives a small heal
    """

    heal_amount = randint(5, 25)
    player.heal_by(heal_amount)
    
    template = PHRASES["events"]["heal"]
    formatted = template.format(amount=heal_amount)
    result = await translate(formatted, language, redis)
    return {"language": language, "type": "heal", "value": heal_amount, "report": result}


async def summon_enemy_event(
    player: Player,
    enemy: Enemy,
    language: languages,
    redis: Redis,
) -> dict:
    """Trigger an enemy encounter.

    :param enemy: optional key to force a specific opponent
    """

    return {"type": "enemy", "value": enemy, "report": None}


async def poison_event(player: Player, language: languages, redis: Redis) -> dict:
    """Placeholder stub; real logic will be added later."""

    return {"type": "poison", "value": 0, "report": None}
