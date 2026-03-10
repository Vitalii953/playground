import pytest

from game_internals.core.gameplay.entities.player import Player
from game_internals.core.schemas.items import (
    Accessory,
    Gear,
    ShieldOnly,
    TwoHanded,
    WeaponAndShield,
    WeaponOnly,
)


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


@pytest.fixture
def gear_factory():
    """Return a piece of gear with reasonable defaults.

    Callers may override the slot or any modifiers via keyword args.
    """

    def _make(slot="helmet", **kwargs) -> Gear:
        return Gear(
            name="gear",
            slot=slot,
            hp_add=kwargs.pop("hp_add", 0),
            speed_add=kwargs.pop("speed_add", 0),
            drop_rate=kwargs.pop("drop_rate", 1.0),
            **kwargs,
        )

    return _make


@pytest.fixture
def weapon_factory():
    """Return a weapon instance appropriate for the requested slot."""

    def _make(slot: str = "one-handed", **kwargs):
        cls = {
            "one-handed": WeaponOnly,
            "one-handed-and-shield": WeaponAndShield,
            "shield": ShieldOnly,
            "two-handed": TwoHanded,
        }[slot]
        # all weapon types expose attack_add/hp_add/drop_rate
        return cls(
            name="weapon",
            slot=slot,
            attack_add=kwargs.pop("attack_add", 0),
            hp_add=kwargs.pop("hp_add", 0),
            drop_rate=kwargs.pop("drop_rate", 1.0),
            **kwargs,
        )

    return _make


@pytest.fixture
def accessory_factory():
    def _make(slot="finger", **kwargs) -> Accessory:
        return Accessory(
            name="acc",
            slot=slot,  # type: ignore[arg-type]
            hp_multiply=kwargs.pop("hp_multiply", 1),
            attack_multiply=kwargs.pop("attack_multiply", 1),
            speed_multiply=kwargs.pop("speed_multiply", None),
            drop_rate=kwargs.pop("drop_rate", 1.0),
            **kwargs,
        )

    return _make


@pytest.fixture
def player():
    """Concrete ``Player`` object for game tests.

    This overrides the generic mock defined in the top-level
    ``tests/conftest.py`` so that equipment manipulation and stat
    calculations exercise real logic.
    """

    return Player(name="Test", hp=100, attack=10, speed=5)
