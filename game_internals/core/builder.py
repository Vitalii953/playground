from __future__ import annotations
from random import choice, choices, randint, random
import logging


log = logging.getLogger(__name__)


def create_player(name: str, language=None) -> Player:  # type: ignore
    """
    IMPORTANT: language selection actually happens when a player is initialized.
    - Language CAN be passed manually or by loading with get_current_language()
    """

    from game.gameplay.entities.player import Player
    from game.config.loader import load_config, get_current_language

    # if it's not passed as argument
    if language is None:
        language = get_current_language()
        log.info(
            f"{name} has been created with {language} language used from previous session"
        )

    # getting it from loader.py
    else:
        log.info(f"{name} has been created with {language} language")

    try:
        config = load_config(language)
    except (ValueError, TypeError, FileNotFoundError):
        log.error(f"invalid language configuration: {language} received")
        raise

    # load_config returns a dictionary. Here, the "game"
    # chunk is needed for general settings (e.g., stats)
    game_settings = config["game"]

    # player is created here using config params
    player = Player(
        name=name,
        hp=game_settings["starting_hp"],
        attack=game_settings["starting_attack"],
        speed=game_settings["starting_speed"],
    )

    log.info(
        f"{name} has been initialized with:\n{player.hp} health;\n{player.attack} attack;\n{player.speed} speed"
    )

    return player


def create_3_paths(floor: int, language: str = None) -> list[dict]:
    """
    Generates 3 paths for player to choose from (config["game"] has it all).
    Returns a list WITH DICTIONARIES

    SO if paths_generated = create_3_paths(...),
    THEN the VALUE during every iteration is considered a
    SEPARATE DICTIONARY

    """

    from game.config.loader import load_config, get_current_language
    from random import shuffle

    if language is None:
        language = get_current_language()

    config = load_config(language)
    lie_chance = config["difficulty"]["lie_chance"]
    danger_increase = config["difficulty"]["probability_scaling"][
        "danger_increase_per_floor"
    ]

    paths = []
    risk_types = ["high_risk", "medium_risk", "low_risk"]  # from config

    for risk in risk_types:  # 3 paths
        base_probs = config["paths"][risk]["base_probabilities"].copy()
        if "enemy" in base_probs:

            enemy_increase = floor * danger_increase
            # cap at 95%
            base_probs["enemy"] = min((base_probs["enemy"] + enemy_increase), 0.95)
            # genius move: if sum of values != 1, MAKE IT 1!
            total = sum(base_probs.values())
            # this formula ensures weights = 1
            base_probs = {k: v / total for k, v in base_probs.items()}
            events = list(base_probs.keys())  # ["enemy", "poison", "heal", etc]
            chances = list(base_probs.values())  # [0.60, 0.15, 0.15, etc]
            actual_event = choices(events, weights=chances, k=1)[0]

            # select hints
            hints = config["paths"][risk]["hints"]
            hint_id = choice(list(hints.keys()))  # "mist"
            hint_text = hints[hint_id]["text"]  # "Something hides in the mist..."

            # lie implementation
            if random() < lie_chance:
                # If risk = "high_risk", lying_risks = ["medium_risk", "low_risk"]
                lying_risks = [rsk for rsk in risk_types if rsk != risk]
                lying_risk = choice(lying_risks)
                # get hints from the other risk level
                lying_hints = config["paths"][lying_risk]["hints"]
                # Pick a random hint from the lying risk
                hint_id = choice(list(lying_hints.keys()))
                hint_text = lying_hints[hint_id]["text"]

                # player sees a LOW RISK (or any other) hint
                # but the actual event is still from HIGH RISK (or any other)

            # storing in a dict
            paths.append(
                {
                    "risk": risk,
                    "hint_id": hint_id,
                    "hint_text": hint_text,
                    "finalized_event": actual_event,
                }
            )

    # shuffling so that randomness appears
    shuffle(paths)
    return paths


def check_milestone(floor: int, language: str = None) -> int:
    """
    Checks if player reached a milestone floor (10, 20, 30, etc).
    Returns coin reward from config, scaled with variance.
    Returns 0 if not a milestone floor.
    """

    from game.config.loader import load_config, get_current_language

    if language is None:
        language = get_current_language()

    config = load_config(language)
    milestone_config = config.get("milestone_coins", {})
    base_rewards = milestone_config.get("base_rewards", {})
    variance = milestone_config.get("variance", 0.15)

    # Check if floor is a milestone (keys can be int or str)
    if floor not in base_rewards and str(floor) not in base_rewards:
        return 0

    base_reward = base_rewards.get(floor) or base_rewards.get(str(floor))
    # Apply variance (±variance%)
    variance_amount = int(base_reward * variance)
    reward = base_reward + randint(-variance_amount, variance_amount)

    log.info(f"Milestone reached at floor {floor}. Reward: {reward} coins")
    return max(reward, 0)  # Ensure non-negative


def create_event(player: Player, chosen_path: dict, language: str = None):  # type: ignore
    """
    Handles all events for both environments and keeps the facade simple and approachable. Events need to be added here if new are implemented
    IMPORTANT: create_3_paths() has to be called SEPARATELY
    """

    from game.gameplay.entities.player import Player
    from game.config.loader import load_config, get_current_language
    from game.menu.menu_terminal import slow_print
    from game.gameplay.events.events import (
        floor_down_event,
        poison_event,
        summon_enemy_event,
        heal_event,
        random_item_event,
        floor_up_event,
        add_coins_event,
    )

    if language is None:
        language = get_current_language()

    # Use the finalized_event from the path (already calculated in create_3_paths)
    finalized_event = chosen_path.get("finalized_event")

    if not finalized_event:
        log.warning(f"No finalized_event in path: {chosen_path}")
        return None

    if finalized_event == "enemy":
        return summon_enemy_event(player)
    elif finalized_event == "poison":
        return poison_event(player)
    elif finalized_event == "floor_down":
        return floor_down_event(player)
    elif finalized_event == "heal":
        return heal_event(player)
    elif finalized_event == "item":
        return random_item_event(player)
    elif finalized_event == "coins":
        return add_coins_event(player)
    elif finalized_event == "floor_up":  # low-risk only
        return floor_up_event(player)
    else:
        log.error(f"Unknown event type: {finalized_event}")
        return None
