import logging


""" 
Menu system for the Dungeon Master game using
terminal interface. 
Provides options to 
- start the game, 
- view guide,
- view statistics,
- access settings,
- and exit the game.
"""


log = logging.getLogger(__name__)


# REF
# menu:
# title: "Dungeon Master"
#  buttons:
# guide: "[0] - GUIDE"
#  start_game: "[1] - START GAME"
# stats: "[2] - STATISTICS"
# settings: "[3] - SETTINGS"
# exit: "[4] - EXIT"

# settings_options: "Choose Language:\n[1] - English\n[2] - French\n[3] - EXIT"

# description: "Welcome to Dungeon Master! This is a simple crawler game where you navigate through floors filled with enemies, traps, and treasures. Choose your path wisely and try to reach the highest floor possible!  Good luck, adventurer!"
# under_development: "This feature is under development. Please check back later!"
# exiting: "Exiting the game. Goodbye!"
# invalid_option: "Invalid option. Please choose a valid option (0-4)."

# end_game: "GAME OVER"
# new_record: "NEW RECORD!"
# choose_option: "Choose an option (0-4): "
# choose_path: "Choose your path (1-3): "


# ================ HELPERS ==================
def wrap_equal(func):
    def wrapper(*args, **kwargs):
        print(f'\n{"="*40}')
        res = func(*args, **kwargs)
        print(f'{"="*40}\n')
        return res

    return wrapper


def wrap_hyphen(func):
    def wrapper(*args, **kwargs):
        print(f'\n{"-"*40}')
        res = func(*args, **kwargs)
        print(f'{"-"*40}\n')
        return res

    return wrapper


def wrap_mountain(func):
    def wrapper(*args, **kwargs):
        print(f'{"/\\"*40}')
        res = func(*args, **kwargs)
        print(f'{"\\/"*40}\n')
        return res

    return wrapper


def slow_print(text: str, delay: float = 0.05, hold: float = 1.5):
    import sys
    import time

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()
    if hold and hold > 0:  # Check if hold is a positive number
        time.sleep(hold)


# ===========================================


def menu():
    from game.builder import create_player
    from game.engine import game_loop
    from game.config.loader import get_current_language, get_menu, set_current_language

    # BUTTONS
    @wrap_equal
    def title(config_menu):
        print(config_menu["title"])

    @wrap_hyphen
    def guide(config_menu):
        print(config_menu["buttons"]["guide"])

    @wrap_hyphen
    def start_game_display(config_menu):
        print(config_menu["buttons"]["start_game"])

    @wrap_hyphen
    def stats(config_menu):
        print(config_menu["buttons"]["stats"])

    @wrap_hyphen
    def settings_display(config_menu):
        print(config_menu["buttons"]["settings"])

    @wrap_hyphen
    def exit_menu(config_menu):
        print(config_menu["buttons"]["exit"])

    while True:
        language = get_current_language()
        config_menu = get_menu(language)  # defaults to english

        title(config_menu)
        guide(config_menu)
        start_game_display(config_menu)
        stats(config_menu)
        settings_display(config_menu)
        exit_menu(config_menu)

        # player chooses their option
        player_choice = input(config_menu["choose_option"])
        if player_choice == "0":
            slow_print(config_menu["description"])

        # start game
        elif player_choice == "1":
            player = create_player(name="player")
            game_loop(player)

        # stats
        elif player_choice == "2":
            slow_print(config_menu["under_development"])

        # settings
        elif player_choice == "3":
            while True:
                print(config_menu["settings_options"])
                lang_option = input("")
                if lang_option == "1":
                    set_current_language("en")
                    config_menu = get_menu("en")  # this reloads cfg
                    slow_print("Language set to English.", hold=1)
                    break
                elif lang_option == "2":
                    set_current_language("fr")
                    config_menu = get_menu("fr")  # this reloads cfg
                    slow_print("Langue définie sur le français.", hold=1)
                    break
                elif lang_option == "3":
                    slow_print("Exiting settings.", hold=1)
                    break
                else:
                    slow_print(
                        "Invalid option. Please choose a valid option (1-3).", hold=1
                    )

        # exit
        elif player_choice == "4":
            slow_print(config_menu["exiting"])
            break

        # invalid option
        else:
            slow_print(config_menu["invalid_option"])
