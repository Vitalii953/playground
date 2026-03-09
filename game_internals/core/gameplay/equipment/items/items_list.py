from game_internals.core.schemas.items import Gear, Accessory, WeaponOnly, WeaponAndShield, ShieldOnly, TwoHanded


# ── weapons ───────────────────────────────────────────────────────────────────

ONE_HANDED: dict[str, WeaponOnly] = {
    "wooden_sword": WeaponOnly(
        name="Wooden Sword", attack_add=5, slot="one-handed", drop_rate=0.50
    ),
    "iron_sword": WeaponOnly(
        name="Iron Sword", attack_add=8, slot="one-handed", drop_rate=0.35
    ),
    "sharp_axe": WeaponOnly(
        name="Sharp Axe", attack_add=12, slot="one-handed", drop_rate=0.25
    ),
}

ONE_HANDED_AND_SHIELD: dict[str, WeaponAndShield] = {
    "wooden_sword_and_shield": WeaponAndShield(
        name="Wooden Sword And Shield",
        attack_add=5,
        hp_add=10,
        slot="one-handed-and-shield",
        drop_rate=0.30,
    ),
    "iron_sword_and_shield": WeaponAndShield(
        name="Iron Sword & Shield",
        attack_add=10,
        hp_add=20,
        slot="one-handed-and-shield",
        drop_rate=0.12,
    ),
    "gladiator_set": WeaponAndShield(
        name="Gladiator Set",
        attack_add=15,
        hp_add=35,
        slot="one-handed-and-shield",
        drop_rate=0.03,
    ),
}

TWO_HANDED: dict[str, TwoHanded] = {
    "steel_hammer": TwoHanded(
        name="Steel Hammer",
        attack_add=14,
        slot="two-handed",
        drop_rate=0.30,
    ),
    "great_sword": TwoHanded(
        name="Great Sword",
        attack_add=20,
        slot="two-handed",
        drop_rate=0.12,
    ),
}

SHIELDS: dict[str, ShieldOnly] = {
    "wooden_shield": ShieldOnly(
        name="Wooden Shield",
        hp_add=8,
        slot="shield",
        drop_rate=0.25,
    ),
    "iron_shield": ShieldOnly(
        name="Iron Shield", hp_add=15, slot="shield", drop_rate=0.12
    ),
    "tower_shield": ShieldOnly(
        name="Tower Shield", hp_add=25, slot="shield", drop_rate=0.05
    ),
}

HELMETS: dict[str, Gear] = {
    "shark_hat": Gear(name="Shark Hat", hp_add=7, slot="helmet", drop_rate=0.50),
    "miner_hat": Gear(name="Miner Hat", hp_add=15, slot="helmet", drop_rate=0.30),
    "box_hat": Gear(name="Box Hat", hp_add=10, slot="helmet", drop_rate=0.35),
    "knight_helmet": Gear(
        name="Knight Helmet", hp_add=20, slot="helmet", drop_rate=0.10
    ),
}

CHESTPLATES: dict[str, Gear] = {
    "leather_armor": Gear(
        name="Leather Armor", hp_add=10, slot="chestplate", drop_rate=0.50
    ),
    "chainmail_armor": Gear(
        name="Chainmail Armor", hp_add=20, slot="chestplate", drop_rate=0.30
    ),
    "iron_armor": Gear(name="Iron Armor", hp_add=35, slot="chestplate", drop_rate=0.15),
    "dragon_scale_armor": Gear(
        name="Dragon Scale Armor", hp_add=50, slot="chestplate", drop_rate=0.01
    ),
}

LEGGINGS: dict[str, Gear] = {
    "leather_leggings": Gear(
        name="Leather Leggings", hp_add=5, slot="leggings", drop_rate=0.50
    ),
    "chainmail_leggings": Gear(
        name="Chainmail Leggings", hp_add=12, slot="leggings", drop_rate=0.30
    ),
    "iron_leggings": Gear(
        name="Iron Leggings", hp_add=25, slot="leggings", drop_rate=0.15
    ),
    "dragon_scale_leggings": Gear(
        name="Dragon Scale Leggings", hp_add=40, slot="leggings", drop_rate=0.01
    ),
}

BOOTS: dict[str, Gear] = {
    "leather_boots": Gear(
        name="Leather Boots", hp_add=0, speed_add=6, slot="boots", drop_rate=0.50
    ),
    "iron_boots": Gear(
        name="Iron Boots", hp_add=5, speed_add=8, slot="boots", drop_rate=0.30
    ),
    "swift_boots": Gear(
        name="Swift Boots", hp_add=0, speed_add=11, slot="boots", drop_rate=0.15
    ),
    "dragon_boots": Gear(
        name="Dragon Boots", hp_add=5, speed_add=10, slot="boots", drop_rate=0.01
    ),
}

RINGS: dict[str, Accessory] = {
    "angel_ring": Accessory(
        name="Angel Ring",
        hp_multiply=1.2,
        attack_multiply=1.2,
        slot="finger",
        drop_rate=0.50,
    ),
    "demonic_ring": Accessory(
        name="Demonic Ring",
        hp_multiply=1.3,
        attack_multiply=1.5,
        slot="finger",
        drop_rate=0.20,
    ),
    "dragon_ring": Accessory(
        name="Dragon Ring",
        hp_multiply=2.0,
        attack_multiply=2.0,
        slot="finger",
        drop_rate=0.01,
    ),
}

# ── full catalog ──────────────────────────────────────────────────────────────

CATALOG: dict[
    str, Gear | WeaponOnly | WeaponAndShield | ShieldOnly | TwoHanded | Accessory
] = {
    **ONE_HANDED,
    **ONE_HANDED_AND_SHIELD,
    **TWO_HANDED,
    **SHIELDS,
    **HELMETS,
    **CHESTPLATES,
    **LEGGINGS,
    **BOOTS,
    **RINGS,
}
# this might be useful for items_operations? Probably, it gives pydantic models right away