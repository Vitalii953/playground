from game_internals.core.schemas.items import Gear, Weapon, Accessory
from game_internals.core.gameplay.equipment.items.items_list import CATALOG 
from typing import Literal, TypeAlias
from random import choices
import logging


logger = logging.getLogger(__name__)


# types for functions
WEIGHTS_TYPES: TypeAlias = Literal["ITEM_WEIGHTS"]
CATEGORIES_TYPES: TypeAlias = Literal[
    "one_handed",             # WEAPON
    "one_handed_shield",      # WEAPON
    "two_handed",             # WEAPON
    "helmets",                # GEAR
    "chestplates",            # GEAR
    "leggings",               # GEAR
    "boots",                  # GEAR
    "rings",                  # ACCESSORY
]

CATEGORIES = (
    "one_handed",
    "one_handed_shield",
    "two_handed",
    "helmets",
    "chestplates",
    "leggings",
    "boots",
    "rings",
)


def pick_rand_item_by_category(category: CATEGORIES_TYPES):
    if category not in CATEGORIES:
        logger.error(
            "Potential bug: invalid category passed for arg 'category': got %s",
            category,
        )
        raise TypeError("Invalid category provided")

    # CATALOG contains all values filtered by the category

    # category is a string, not the actual category
    category_keys = CATALOG.keys()
    # all_items_in_category = [item for item in CATALOG.items() if isinstance(item, category)]  
    print(category_keys)
    



def pick_random_item() -> tuple[str, Gear | Weapon | Accessory]:
    """Pick a category by chance, then a weighted item within it."""
    pass


if __name__ == "__main__":
    pick_rand_item_by_category("boots")