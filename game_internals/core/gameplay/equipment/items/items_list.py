from game_internals.core.schemas.items import Gear, Weapon, Accessory



# ── weapons ───────────────────────────────────────────────────────────────────

SWORDS: dict[str, Weapon] = {
    "wooden_sword": Weapon(name="Wooden Sword", attack_add=5, slot="one-handed"),
    "iron_sword": Weapon(name="Iron Sword", attack_add=8, slot="one-handed"),
    "sharp_axe": Weapon(name="Sharp Axe", attack_add=3, slot="one-handed"),
    "steel_hammer": Weapon(name="Steel Hammer", attack_add=4, slot="two-handed"),
}

# ── helmets ───────────────────────────────────────────────────────────────────

HELMETS: dict[str, Gear] = {
    "shark_hat": Gear(name="Shark Hat", hp_add=7, slot="helmet"),
    "miner_hat": Gear(name="Miner Hat", hp_add=15, slot="helmet"),
    "box_hat": Gear(name="Box Hat", hp_add=10, slot="helmet"),
    "knight_helmet": Gear(name="Knight Helmet", hp_add=20, slot="helmet"),
}

# ── chests ────────────────────────────────────────────────────────────────────

CHESTS: dict[str, Gear] = {
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

# ── wings (accessories) ───────────────────────────────────────────────────────

WINGS: dict[str, Accessory] = {
    "angel_wings": Accessory(
        name="Angel Wings", hp_multiply=1.2, attack_multiply=1.2, slot="finger"
    ),
    "demonic_wings": Accessory(
        name="Demonic Wings", hp_multiply=1.3, attack_multiply=1.5, slot="finger"
    ),
    "dragon_wings": Accessory(
        name="Dragon Wings", hp_multiply=2.0, attack_multiply=2.0, slot="finger"
    ),
}

# ── full catalog ──────────────────────────────────────────────────────────────

CATALOG: dict[str, Gear | Weapon | Accessory] = {
    **SWORDS,
    **HELMETS,
    **CHESTS,
    **BOOTS,
    **WINGS,
}

# when need to access any items inside dicts
ALL_ITEMS_FLAT = [
    *SWORDS.values(),
    *HELMETS.values(),
    *CHESTS.values(),
    *BOOTS.values(),
    *WINGS.values(),
]

# by chances 
CATEGORY_CHANCES = [
    0.4,
    0.25,
    0.2,
    0.149,
    0.001,
]

# WIP. Need to wip them all together
