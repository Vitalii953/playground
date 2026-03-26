"""
handles everything related to picking an event, which is the core of the gameplay loop
contains all necessary logic to pick an event, inject necessary arguments, and execute it
all repetitive logic is handled either here or in events themselves while respecting consistency
"""

import inspect
import logging
from random import choice
from redis.asyncio import Redis
from game_internals.core.gameplay.entities.player import Player
from game_internals.core.schemas.game_settings import languages
from game_internals.core.phrases import PHRASES
from game_internals.events import ALL_EVENTS
from backend.services.translator.translation_service import translate


logger = logging.getLogger(__name__)


async def resolve_pending_action(response: dict, player: Player, language: languages, redis: Redis) -> str | None:
    """
    THIS CAN ONLY BE CALLED BY FRONTEND 
    when it receives a pending action with 'needs_input' field
    response should look close to this, the important field is 'needs_input'

    return {
        "language": language,
        "type": "random_item",
        "value": item.model_dump(),
        "report": result,
        "needs_input": True,
        "decision": "equip"     #and this would be the new field FROM FRONTEND (can be "equip" or "reject")
    }
    """

    phrases = PHRASES["game_loop"]["pending_actions"]
    
    if "needs_input" not in response.keys():
        logger.warning("Trying to resolve a pending action that doesn't require input. May be a bug.")
        return
    
    # equip item
    if response["type"] == "random_item" and response["decision"] == "equip":
        result = player.equip(response["value"])   # returns True
        if result: 
            phrase = phrases["equipped_successfully"].format(item_name=response["value"]["name"])
            translated = await translate(phrase, language, redis)
            player.mount_floor(1)
            return translated
        
    # sskip item
    elif response["type"] == "random_item" and response["decision"] == "reject":
        phrase = phrases["rejected_item"].format(item_name=response["value"]["name"])
        translated = await translate(phrase, language, redis)
        player.mount_floor(1)
        return translated
        
        


async def pick_event(player: Player, language: languages, redis: Redis):
    """
    abstracts away the logic of picking an event
    but i tried to keep it intuitive
    """

    events = ALL_EVENTS
    chosen_key = choice(list(events.keys()))

    # They all require different arguments, i inject dynamically
    chosen_event = events[chosen_key]  # function object

    kwargs = {}
    sig = inspect.signature(chosen_event)
    if "player" in sig.parameters:
        kwargs["player"] = player
    if "language" in sig.parameters:
        kwargs["language"] = language
    if "redis" in sig.parameters:
        kwargs["redis"] = redis

    return await chosen_event(**kwargs)


async def go_one_step(player: Player, language: languages, redis: Redis):
    """
    some checks may be excessive, but i want to keep it secure and easy to debug
    frontend is responsible for calling extra function if it has parameter 'needs_input'
    """

    if player.is_alive():
        result = await pick_event(player, language, redis)

        # If the event requires a front-end decision, short-circuit and return
        # the pending action. The caller is responsible for storing the state
        # and invoking the appropriate resolver (e.g. equip or reject).
        if isinstance(result, dict) and result.get("needs_input"):
            # let frontend handle it
            return
        
        player.mount_floor(1)
        return result
    
    else:
        # this shouldn't happen (if it does then main loop is the problem)
        logger.error("Player is dead, can't go one step. May be a bug")
        raise Exception("Player is dead, can't go one step")


