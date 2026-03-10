from unittest.mock import patch

import pytest

from game_internals.core.gameplay.equipment.items_operations import (
    CATEGORIES,
    pick_rand_item_by_category,
    pick_random_item,
)
from game_internals.core.schemas.items import (
    Accessory,
    Gear,
    ShieldOnly,
    TwoHanded,
    WeaponAndShield,
    WeaponOnly,
)

# ── pick_rand_item_by_category ──────────────────────────────────────────────


class TestPickRandItemByCategory:
    """Tests for pick_rand_item_by_category function"""

    def test_valid_category_returns_item_from_catalog(self, sample_catalog):
        """should return a valid item when given a valid category"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            result = pick_rand_item_by_category("one-handed")

            assert result is not None
            assert result.slot == "one-handed"

    def test_valid_category_returns_pydantic_model(self, sample_catalog):
        """returned item should be a validated pydantic model"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            result = pick_rand_item_by_category("helmet")

            assert isinstance(
                result,
                (Gear, WeaponOnly, Accessory, WeaponAndShield, ShieldOnly, TwoHanded),
            )
            assert hasattr(result, "name")
            assert hasattr(result, "slot")

    def test_invalid_category_raises_type_error(self, sample_catalog):
        """should raise TypeError for invalid category"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            with pytest.raises(TypeError, match="Invalid category provided"):
                pick_rand_item_by_category("invalid_category")  # type: ignore

    def test_all_valid_categories_work(self, sample_catalog):
        """all CATEGORIES should be valid and not raise"""
        # Create a catalog with items for each category
        extended_catalog = {
            "item_1h": WeaponOnly(
                name="1h", slot="one-handed", attack_add=10, drop_rate=0.5
            ),
            "item_1h_shield": WeaponAndShield(
                name="1h+shield",
                slot="one-handed-and-shield",
                attack_add=8,
                hp_add=5,
                drop_rate=0.5,
            ),
            "item_2h": TwoHanded(
                name="2h", slot="two-handed", attack_add=20, drop_rate=0.5
            ),
            "item_shield": ShieldOnly(
                name="shield", slot="shield", hp_add=5, drop_rate=0.5
            ),
            "item_helmet": Gear(name="helmet", slot="helmet", hp_add=5, drop_rate=0.5),
            "item_chest": Gear(
                name="chest", slot="chestplate", hp_add=10, drop_rate=0.5
            ),
            "item_legs": Gear(name="legs", slot="leggings", hp_add=7, drop_rate=0.5),
            "item_boots": Gear(name="boots", slot="boots", hp_add=3, drop_rate=0.5),
            "item_ring": Accessory(
                name="ring",
                slot="finger",
                hp_multiply=1.0,
                attack_multiply=1.0,
                drop_rate=0.5,
            ),
        }

        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            extended_catalog,
        ):
            for category in CATEGORIES:
                result = pick_rand_item_by_category(category)
                assert result.slot == category

    def test_category_filtering_works_correctly(self, sample_catalog):
        """should only return items matching the requested category"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            result = pick_rand_item_by_category("helmet")

            assert result.name in ["Iron Helmet", "Steel Helmet"]
            assert result.slot == "helmet"

    def test_weighted_selection_respects_drop_rates(self):
        """weighted selection should favor higher drop_rate items more often"""
        # Item A has 0.9 drop rate, Item B has 0.1
        # Run 100 times, Item A should appear ~90 times
        catalog = {
            "high_rate": WeaponOnly(
                name="Common", slot="one-handed", attack_add=5, drop_rate=0.9
            ),
            "low_rate": WeaponOnly(
                name="Rare", slot="one-handed", attack_add=10, drop_rate=0.1
            ),
        }

        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            catalog,
        ):
            results = [pick_rand_item_by_category("one-handed") for _ in range(100)]
            common_count = sum(1 for r in results if r.name == "Common")

            # With 90% drop rate, we expect ~90 out of 100
            assert 70 < common_count <= 100


# ── pick_random_item ────────────────────────────────────────────────────────


class TestPickRandomItem:
    """Tests for pick_random_item function"""

    def test_returns_item_from_catalog(self, sample_catalog):
        """should return a valid item from catalog"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            result = pick_random_item()

            assert result is not None
            assert result.name in [
                "Iron Sword",
                "Steel Sword",
                "Iron Helmet",
                "Steel Helmet",
            ]

    def test_returns_pydantic_model(self, sample_catalog):
        """returned item should be a validated pydantic model"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            result = pick_random_item()

            assert isinstance(
                result,
                (Gear, WeaponOnly, Accessory, WeaponAndShield, ShieldOnly, TwoHanded),
            )
            assert hasattr(result, "name")
            assert hasattr(result, "slot")
            assert hasattr(result, "drop_rate")

    def test_multiple_calls_can_return_different_items(self, sample_catalog):
        """multiple calls should be able to return different items"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            results = set(pick_random_item().name for _ in range(50))

            # With 50 calls and 4 items, should get variety
            assert len(results) > 1

    def test_respects_drop_rate_weights_in_full_catalog(self):
        """full catalog selection should favor items with higher drop_rate"""
        catalog = {
            "common": WeaponOnly(
                name="Common", slot="one-handed", attack_add=5, drop_rate=0.8
            ),
            "rare": WeaponOnly(
                name="Rare", slot="one-handed", attack_add=10, drop_rate=0.2
            ),
        }

        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            catalog,
        ):
            results = [pick_random_item() for _ in range(100)]
            common_count = sum(1 for r in results if r.name == "Common")

            # With 80% drop rate, expect ~80 out of 100
            assert 60 < common_count <= 100

    def test_returns_consistent_item_types(self, sample_catalog):
        """all returned items should have required attributes"""
        with patch(
            "game_internals.core.gameplay.equipment.items.items_operations.CATALOG",
            sample_catalog,
        ):
            for _ in range(20):
                result = pick_random_item()

                assert hasattr(result, "name")
                assert isinstance(result.name, str)
                assert hasattr(result, "slot")
                assert isinstance(result.slot, str)
                assert hasattr(result, "drop_rate")
                assert 0 <= result.drop_rate <= 1
