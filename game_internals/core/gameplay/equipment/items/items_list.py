from game_internals.core.schemas.items import Gear, Weapon, Accessory


# ── weapons ───────────────────────────────────────────────────────────────────

WEAPONS: dict[str, Weapon] = {
    # one-handed, no shield
    "wooden_sword": Weapon(
        name="Wooden Sword", attack_add=5, hp_add=None, slot="one-handed"
    ),
    "iron_sword": Weapon(
        name="Iron Sword", attack_add=8, hp_add=None, slot="one-handed"
    ),
    "sharp_axe": Weapon(
        name="Sharp Axe", attack_add=12, hp_add=None, slot="one-handed"
    ),
    # one-handed + shield combos
    "wooden_sword_and_shield": Weapon(
        name="Wooden Sword And Shield",
        attack_add=5,
        hp_add=10,
        slot="one-handed",
    ),
    "iron_sword_and_shield": Weapon(
        name="Iron Sword & Shield", attack_add=10, hp_add=20, slot="one-handed"
    ),
    "gladiator_set": Weapon(
        name="Gladiator Set", attack_add=15, hp_add=35, slot="one-handed"
    ),
    # two-handed
    "steel_hammer": Weapon(
        name="Steel Hammer", attack_add=14, hp_add=None, slot="two-handed"
    ),
    "great_sword": Weapon(
        name="Great Sword", attack_add=20, hp_add=None, slot="two-handed"
    ),
    # shields
    "wooden_shield": Weapon(
        name="Wooden Shield", attack_add=None, hp_add=8, slot="shield"
    ),
    "iron_shield": Weapon(
        name="Iron Shield", attack_add=None, hp_add=15, slot="shield"
    ),
    "tower_shield": Weapon(
        name="Tower Shield", attack_add=None, hp_add=25, slot="shield"
    ),
}

# ── helmets ───────────────────────────────────────────────────────────────────

HELMETS: dict[str, Gear] = {
    "shark_hat": Gear(name="Shark Hat", hp_add=7, slot="helmet"),
    "miner_hat": Gear(name="Miner Hat", hp_add=15, slot="helmet"),
    "box_hat": Gear(name="Box Hat", hp_add=10, slot="helmet"),
    "knight_helmet": Gear(name="Knight Helmet", hp_add=20, slot="helmet"),
}

# ── chests ────────────────────────────────────────────────────────────────────

CHESTPLATES: dict[str, Gear] = {
    "leather_armor": Gear(name="Leather Armor", hp_add=10, slot="chestplate"),
    "chainmail_armor": Gear(name="Chainmail Armor", hp_add=20, slot="chestplate"),
    "iron_armor": Gear(name="Iron Armor", hp_add=35, slot="chestplate"),
    "dragon_scale_armor": Gear(name="Dragon Scale Armor", hp_add=50, slot="chestplate"),
}

# ── boots ─────────────────────────────────────────────────────────────────────

BOOTS: dict[str, Gear] = {
    "leather_boots": Gear(name="Leather Boots", hp_add=0, speed_add=6, slot="boots"),
    "iron_boots": Gear(name="Iron Boots", hp_add=5, speed_add=8, slot="boots"),
    "swift_boots": Gear(name="Swift Boots", hp_add=0, speed_add=11, slot="boots"),
    "dragon_boots": Gear(name="Dragon Boots", hp_add=5, speed_add=10, slot="boots"),
}

RINGS: dict[str, Accessory] = {
    "angel_ring": Accessory(
        name="Angel Ring", hp_multiply=1.2, attack_multiply=1.2, slot="finger"
    ),
    "demonic_ring": Accessory(
        name="Demonic Ring", hp_multiply=1.3, attack_multiply=1.5, slot="finger"
    ),
    "dragon_ring": Accessory(
        name="Dragon Ring", hp_multiply=2.0, attack_multiply=2.0, slot="finger"
    ),
}


# ── full catalog ──────────────────────────────────────────────────────────────
CATALOG: dict[str, Gear | Weapon | Accessory] = {
    **WEAPONS,
    **HELMETS,
    **CHESTPLATES,
    **BOOTS,
    **RINGS,
}

ITEM_WEIGHTS: dict[str, dict[str, float]] = {
    # weapons — one-handed
    "one_handed": {
        "wooden_sword": 0.40,
        "iron_sword": 0.30,
        "sharp_axe": 0.20,
    },
    # weapons — one-handed + shield
    "one_handed_shield": {  # this name doesn't change anything outside, its for funcs
        "wooden_sword_and_shield": 0.30,
        "iron_sword_and_shield": 0.15,
        "gladiator_set": 0.05,
    },
    # weapons — two-handed
    "two_handed": {
        "steel_hammer": 0.25,
        "great_sword": 0.10,
    },
    # helmets
    "helmets": {
        "shark_hat": 0.40,
        "miner_hat": 0.25,
        "box_hat": 0.30,
        "knight_helmet": 0.05,
    },
    # chestplates
    "chestplates": {
        "leather_armor": 0.40,
        "chainmail_armor": 0.30,
        "iron_armor": 0.20,
        "dragon_scale_armor": 0.01,
    },
    # boots
    "boots": {
        "leather_boots": 0.40,
        "iron_boots": 0.30,
        "swift_boots": 0.20,
        "dragon_boots": 0.10,
    },
    # rings
    "rings": {
        "angel_ring": 0.60,
        "demonic_ring": 0.30,
        "dragon_ring": 0.001,    # the rarest item, exclusive one
    },
}
