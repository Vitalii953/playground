from game_internals.core.schemas.items import (
    Gear,
    Accessory,
    WeaponOnly,
    WeaponAndShield,
    ShieldOnly,
    TwoHanded,
)
from game_internals.core.gameplay.equipment.items.items_list import CATALOG, CATEGORIES, CATEGORIES_TYPES
from random import choices
import logging


logger = logging.getLogger(__name__)


def pick_rand_item_by_category(
    category: CATEGORIES_TYPES,
) -> Gear | Accessory | WeaponOnly | WeaponAndShield | ShieldOnly | TwoHanded:
    if category not in CATEGORIES:
        # in dev this will raise, but if not tested, logs are helpful
        logger.error(
            "Potential bug: invalid category passed for arg 'category': got %s",
            category,
        )
        raise TypeError("Invalid category provided")

    # CATALOG contains all values filtered by the category

    category_items = {k: v for k, v in CATALOG.items() if v.slot == category}
    chosen_key = choices(
        list(category_items.keys()),
        weights=[v.drop_rate for v in category_items.values()],
        k=1,
    )[0]
    final_item = category_items[chosen_key]

    return final_item  # validated pydantic model


def pick_random_item() -> (
    Gear | Accessory | WeaponOnly | WeaponAndShield | ShieldOnly | TwoHanded
):
    """
    same logic but not choosing category here
    """
    chosen_key = choices(
        list(CATALOG.keys()),
        weights=[v.drop_rate for v in CATALOG.values()],
        k=1,
    )[0]
    final_item = CATALOG[chosen_key]

    return final_item  # validated pydantic model
