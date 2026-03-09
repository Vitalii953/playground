import pytest

from game_internals.core.schemas.items import Gear, WeaponOnly


@pytest.fixture
def sample_catalog():
    """Mock CATALOG with sample items for testing"""
    catalog = {
        "iron_sword": WeaponOnly(
            name="Iron Sword",
            slot="one-handed",
            attack_add=8,
            drop_rate=0.5,
        ),
        "steel_sword": WeaponOnly(
            name="Steel Sword",
            slot="one-handed",
            attack_add=15,
            drop_rate=0.3,
        ),
        "iron_helmet": Gear(
            name="Iron Helmet",
            slot="helmet",
            hp_add=5,
            drop_rate=0.4,
        ),
        "steel_helmet": Gear(
            name="Steel Helmet",
            slot="helmet",
            hp_add=8,
            drop_rate=0.2,
        ),
    }
    return catalog
