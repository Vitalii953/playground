"""
turn logic handles floor escalation, so floor up and down events do not take 
this into account. phrases.py explain it better, 
but basically, if you go up, you go up twice, and if you go down, 
you fall down but then recover and find another way up
"""

from redis.asyncio import Redis
from backend.services.translator.translation_service import translate
from game_internals.core.gameplay.entities.player import Player
from game_internals.core.gameplay.equipment.items_operations import pick_random_item
from game_internals.core.phrases import PHRASES
from game_internals.core.schemas.game_settings import languages
from random import randint, choices
from game_internals.core.gameplay.entities.enemies_list import ALL_ENEMIES


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

    return {
        "language": language,
        "type": "add_coins",
        "value": coin_amount,
        "report": result,
    }


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
    return {
        "language": language,
        "type": "heal",
        "value": heal_amount,
        "report": result,
    }


async def fight_summoned_enemy_event(
    player: Player,
    language: languages,
    redis: Redis,
) -> dict:
    """
    Spawn and fight an enemy
    Handles the combat too to avoid inconsistencies and return the result to the frontend
    Game loop should handle finishing the loop if player is dead
    """

    chosen_key = choices(list(ALL_ENEMIES.keys()), k=1)[0]
    enemy = ALL_ENEMIES[chosen_key]()

    report = []
    
    template = await translate(PHRASES["events"]["summon_enemy"], language, redis)
    hit_enemy_template = await translate(PHRASES["game_loop"]["hit_enemy"], language, redis)
    hit_player_template = await translate(PHRASES["game_loop"]["hit_player"], language, redis)


    # fight enemy
    while enemy.is_alive() and player.is_alive():
        # player hits first
        hit_enemy = player.attack_(enemy)
        report.append(f"{hit_enemy_template}{hit_enemy}\n")
        # enemy hits second
        if enemy.is_alive():
            hit_player = enemy.attack_(player)
            report.append(f"{hit_player_template}{hit_player}\n")
    # loop ended - someone is dead
    if not player.is_alive():
        player_survived = False
        template = PHRASES["game_loop"]["player_dead"]
        result = await translate(template, language, redis)
    elif not enemy.is_alive():
        player_survived = True

        coins_loot = enemy.die()
        player.add_coins(coins_loot)

        template = PHRASES["game_loop"]["enemy_dead"]
        result = await translate(template, language, redis)

    return {
        "language": language,
        "type": "summon_enemy",
        "value": vars(enemy),
        "report": report,
        "player_state": player_survived,
        "result": result,
    }


async def poison_event(player: Player, language: languages, redis: Redis) -> dict:
    """
    Poison player
    """
    hp_lost = 0
    for _ in range(3):
        damage_factor = randint(1, 4)
        player.current_hp = max(0, player.current_hp - damage_factor)
        hp_lost += damage_factor

    template = PHRASES["events"]["poison"]
    formatted = template.format(HP=hp_lost)
    result = await translate(formatted, language, redis)

    return {"language": language, "type": "poison", "value": hp_lost, "report": result}


# mapping for turn logic
ALL_EVENTS = {
    "offer_random_item": offer_random_item_event,
    "floor_up": floor_up_event,
    "add_coins": add_coins_event,
    "floor_down": floor_down_event,
    "heal": heal_event,
    "fight_summoned_enemy": fight_summoned_enemy_event,
    "poison": poison_event,
}