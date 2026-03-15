from game_internals.events import ALL_EVENTS
from random import choice
from game_internals.core.gameplay.entities.enemy import Enemy
from game_internals.core.gameplay.entities.player import Player
from backend.core.redis import get_redis    




def pick_event():
    events = ALL_EVENTS
    chosen_key = choice(list(events.keys()))
    # below is a function. They all require different arguments, i inject dynamically
    chosen_event = events[chosen_key]()
    return chosen_key, chosen_event