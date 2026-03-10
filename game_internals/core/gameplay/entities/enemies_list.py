from game_internals.core.gameplay.entities.enemy import Enemy 
from random import randint as ri


def create_rogue() -> Enemy:
    return Enemy(
        name="rogue", hp=ri(25, 35), attack=ri(8, 25), speed=ri(5, 25), coins_loot=ri(2, 5)
    )


def create_bandit() -> Enemy:
    return Enemy(
        name="bandit", hp=ri(30, 40), attack=ri(10, 35), speed=ri(4, 20), coins_loot=ri(3, 6)
    )


def create_thief() -> Enemy:
    return Enemy(
        name="thief", hp=ri(20, 30), attack=ri(7, 30), speed=ri(8, 28), coins_loot=ri(1, 4)
    )


def create_mercenary() -> Enemy:
    return Enemy(
        name="mercenary",
        hp=ri(35, 50),
        attack=ri(12, 35),
        speed=ri(3, 15),
        coins_loot=ri(5, 10),
    )


def create_assassin() -> Enemy:
    return Enemy(
        name="assassin",
        hp=ri(18, 25),
        attack=ri(15, 40),
        speed=ri(10, 30),
        coins_loot=ri(2, 7),
    )


def create_goblin() -> Enemy:
    return Enemy(
        name="goblin", hp=ri(15, 25), attack=ri(5, 8), speed=ri(6, 12), coins_loot=ri(1, 3)
    )


def create_orc() -> Enemy:
    return Enemy(
        name="orc", hp=ri(40, 60), attack=ri(10, 20), speed=ri(3, 8), coins_loot=ri(4, 8)
    )


def create_troll() -> Enemy:
    return Enemy(
        name="troll", hp=ri(60, 80), attack=ri(12, 22), speed=ri(2, 6), coins_loot=ri(5, 10)
    )


def create_skeleton() -> Enemy:
    return Enemy(
        name="skeleton", hp=ri(20, 30), attack=ri(6, 15), speed=ri(4, 12), coins_loot=ri(1, 4)
    )


def create_dragon() -> Enemy:
    return Enemy(
        name="dragon",
        hp=ri(100, 150),
        attack=ri(20, 30),
        speed=ri(8, 15),
        coins_loot=ri(10, 20),
    )


HUMANOIDS = {
    "rogue": create_rogue,
    "bandit": create_bandit,
    "thief": create_thief,
    "mercenary": create_mercenary,
    "assassin": create_assassin,
}

MONSTERS = {
    "goblin": create_goblin,
    "orc": create_orc,
    "troll": create_troll,
    "skeleton": create_skeleton,
    "dragon": create_dragon,
}

# fine for general loop
ALL_ENEMIES = {**HUMANOIDS,
               **MONSTERS,}