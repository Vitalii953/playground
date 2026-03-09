from game_internals.core.schemas.items import Gear, Weapon, Accessory
from game_internals.core.gameplay.equipment.items.items_list import (
    ITEM_WEIGHTS,
)
from typing import Literal, TypeAlias
from random import choices
import logging


logger = logging.getLogger(__name__)


# types for functions
WEIGHTS_TYPES: TypeAlias = Literal["ITEM_WEIGHTS"]
CATEGORIES_TYPES: TypeAlias = Literal[
    "one_handed",
    "one_handed_shield",
    "two_handed",
    "helmets",
    "chestplates",
    "boots",
    "rings",
]

CATEGORIES = (
    "one_handed",
    "one_handed_shield",
    "two_handed",
    "helmets",
    "chestplates",
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

    _items = ITEM_WEIGHTS  
    extracted_keys = list(_items[category].keys())
    extracted_weights = list(ITEM_WEIGHTS[category].values())

    item = choices(extracted_keys, weights=extracted_weights, k=1)[0]   # extracts a string, not pydantic model
    # i take this string, the category, and look up its values 
    # in items, names are defines as dictionary keys without snake_cases and with title case 



    print(item)
    print(type(item))
    



def pick_random_item() -> tuple[str, Gear | Weapon | Accessory]:
    """Pick a category by chance, then a weighted item within it."""
    pass


if __name__ == "__main__":
    pick_rand_item_by_category("boots")