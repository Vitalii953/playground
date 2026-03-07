from game.gameplay.equipment.items.item import Item  # circular import not possible here

# # # WEAPONS # # #
SWORDS = {
    "wooden_sword": Item("wooden sword", "weapon", attack_add=5),
    "iron_sword": Item("iron sword", "weapon", attack_add=5),
    "sharp_axe": Item("sharp axe", "weapon", attack_multiply=1.05, attack_add=3),
    "steel_hammer": Item("steel hammer", "weapon", attack_multiply=1.3, attack_add=4),
}

# # # HELMETS # # #
HELMETS = {
    "shark_hat": Item("shark hat", "helmet", hp_add=7),
    "miner_hat": Item("miner hat", "helmet", hp_multiply=1.03, hp_add=15),
    "box_hat": Item("box hat", "helmet", hp_add=10),
    "knight_helmet": Item("knight helmet", "helmet", hp_multiply=1.8),
}

# # # CHESTS # # #
CHESTS = {
    "leather_armor": Item("leather armor", "chest", hp_add=10),
    "chainmail_armor": Item("chainmail armor", "chest", hp_multiply=1.2),
    "iron_armor": Item("iron armor", "chest", hp_multiply=1.5, hp_add=20),
    "dragon_scale_armor": Item("dragon scale armor", "chest", hp_multiply=2, hp_add=50),
}

# # # BOOTS # # #
BOOTS = {
    "leather_boots": Item("leather boots", "boots", speed=6),
    "iron_boots": Item("iron boots", "boots", speed=8, hp_add=5),
    "swift_boots": Item("swift boots", "boots", speed=11),
    "dragon_boots": Item("dragon boots", "boots", speed=10, hp_multiply=1.1),
}

# # # WINGS # # #
WINGS = {
    "angel_wings": Item(
        "angel wings", "wings", attack_multiply=1.2, hp_multiply=1.2, speed=16
    ),
    "demonic_wings": Item(
        "demonic wings", "wings", attack_multiply=1.5, hp_multiply=1.3, speed=14
    ),
    "dragon_wings": Item(
        "dragon wings", "wings", attack_multiply=2, hp_multiply=2, speed=10
    ),
}

# when need to access item by type
ALL_ITEMS = {
    "swords": SWORDS,
    "helmets": HELMETS,
    "chests": CHESTS,
    "boots": BOOTS,
    "wings": WINGS,
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
CATEGORY_CHANCES = {
    "swords": 0.4,
    "helmets": 0.25,
    "chests": 0.2,
    "boots": 0.149,
    "wings": 0.001,
}
