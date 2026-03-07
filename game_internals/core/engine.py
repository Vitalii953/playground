from random import random, choice


def game_loop(player: Player, language: str = None): 
    """
    Brain of the game.

    "risk": risk,
    "hint_id": hint_id,     #(mist, blood_stains, ...)
    "hint_text": hint_text  -> what is displayed in this func

    Check builder.py (create_3_paths) for better comprehension
    """

    from game.config.loader import load_config, get_current_language, get_game_loop
    from game.builder import create_3_paths, check_milestone, create_event
    from game.gameplay.entities.player import Player
    from game.menu.menu_terminal import slow_print
    import time

    log.info(f"{player.name}'s game_loop initialized at floor {player.floor}")

    cfg = get_game_loop(language)
    player.start_timer()

    turn_count = 0

    while player.is_alive():
        turn_count += 1

        # Display current status (floor should reflect the current state)
        slow_print(cfg["floor_now"].format(player.floor), delay=0.02, hold=0.5)
        slow_print(
            cfg["hp_coins_now"].format(int(player.hp), player.coins),
            delay=0.02,
            hold=0.5,
        )

        # Generate and show path options
        paths_gen = create_3_paths(player.floor, language)
        slow_print(cfg["choose_your_path"], delay=0.02, hold=0.3)

        # Display each path with its risk level and hint
        for idx, path in enumerate(paths_gen, 1):
            risk_key = path["risk"]
            full_config = load_config(language)
            risk_display = full_config.get("risk_labels", {}).get(
                risk_key, risk_key.replace("_", " ").title()
            )
            slow_print(
                cfg["choose_your_path_message"].format(
                    idx, risk_display, path["hint_text"]
                ),
                delay=0.01,
                hold=0.2,
            )

        # Get and validate player's path choice
        while True:
            try:
                choice_input = input(cfg["enter_your_choice"])
                path_index = int(choice_input) - 1
                if 0 <= path_index < len(paths_gen):
                    break
                else:
                    slow_print(cfg["invalid_input"], delay=0.05, hold=0.5)
            except (ValueError, TypeError):
                slow_print(cfg["invalid_input"], delay=0.05, hold=0.5)

        # Process the chosen path and create event
        path_choice = paths_gen[path_index]
        log.info(
            f"Turn {turn_count}: {player.name} chose path with risk '{path_choice['risk']}' and hint '{path_choice['hint_id']}'"
        )

        # Store HP before event to track if damage was taken
        hp_before = player.hp
        floor_before = player.floor

        # Execute the event
        event_result = create_event(player, path_choice, language)

        # Handle event results and display messages
        if not event_result:
            log.warning(f"Empty event result for path: {path_choice}")
            slow_print(cfg["event_fallback"], delay=0.05, hold=0.8)
            continue

        event_type = event_result.get("type", "unknown")
        event_value = event_result.get("value", "")

        log.info(
            f"Turn {turn_count}: Event '{event_type}' occurred with value '{event_value}'. Player HP: {hp_before} → {player.hp}, Floor: {floor_before} → {player.floor}"
        )

        # Display event outcome (use hint-specific message if available, or generic)
        hint_id = path_choice.get("hint_id", "")
        hint_config = None

        # Try to get specific message for this hint+event combo
        try:
            risk = path_choice["risk"]
            hints = load_config(language)["paths"][risk]["hints"]
            if hint_id in hints and event_type in hints[hint_id].get("messages", {}):
                hint_config = hints[hint_id]["messages"][event_type]
                slow_print(hint_config, delay=0.03, hold=0.8)
        except (KeyError, IndexError):
            pass

        # If no specific hint message, try generic event message
        if not hint_config:
            try:
                event_messages = cfg.get("event_messages", {})
                if event_type in event_messages:
                    slow_print(event_messages[event_type], delay=0.03, hold=0.8)
                else:
                    slow_print(cfg["event_fallback"], delay=0.05, hold=0.8)
            except KeyError:
                slow_print(cfg["event_fallback"], delay=0.05, hold=0.8)

        # Display combat results if applicable
        if event_type == "enemy" and "report" in event_result:
            report = event_result["report"]
            enemy_name = event_result["value"]
            if report.get("winner") == player.name:
                slow_print(
                    cfg["victory_message"].format(enemy_name), delay=0.03, hold=0.5
                )
            else:
                slow_print(
                    cfg["defeat_message"].format(enemy_name), delay=0.03, hold=0.5
                )

        # natural floor progression
        if event_type not in ("floor_up", "floor_down"):
            player.floor += 1

        # Check for milestone coins after floor change
        if event_type in ("floor_up", "floor_down") or player.floor != floor_before:
            milestone_reward = check_milestone(player.floor, language)
            if milestone_reward > 0:
                player.coins += milestone_reward
                slow_print(
                    cfg["milestone_message"].format(milestone_reward),
                    delay=0.04,
                    hold=1.0,
                )
                log.info(
                    f"{player.name} reached milestone floor {player.floor} and gained {milestone_reward} coins"
                )

        # display updated status (now works)
        slow_print(
            cfg["hp_coins_now"].format(int(player.hp), player.coins),
            delay=0.02,
            hold=0.5,
        )

        # check if dead
        if not player.is_alive():
            slow_print(
                cfg.get("player_death", "You have fallen..."), delay=0.05, hold=1.0
            )
            log.info(
                f"{player.name} died on floor {player.floor} with {int(player.hp)} HP"
            )
            break

        time.sleep(0.5)

    # end of run
    player.end_run()
    slow_print(f"\n{cfg['end_game']}", delay=0.05, hold=1.0)

    if player.best_run:
        slow_print(cfg["new_record"], delay=0.05, hold=1.0)
        slow_print(
            cfg["best_run_message"].format(player.best_run[0], player.best_run[1]),
            delay=0.03,
            hold=1.0,
        )

    log.info(
        f"{player.name}'s run ended after {turn_count} turns. Best floor: {player.best_run[0] if player.best_run else 0}"
    )
