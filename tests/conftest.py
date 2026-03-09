import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.models.players import Player
from backend.services.game_settings import GameSettingsService


@pytest.fixture
def player():
    p = MagicMock(spec=Player)
    p.id = uuid.uuid4()
    p.preferences = {}
    return p


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)  # cache miss by default
    redis.set = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_mymemory_api_response():
    """Mock response from MyMemory translation API"""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {
        "responseData": {"translatedText": "Bonjour le monde", "match": 1.0},
        "responseStatus": 200,
    }
    return response


@pytest.fixture
def mock_postgres_db():
    """Mock async PostgreSQL database session"""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def game_settings_service(mock_postgres_db, mock_redis):
    """GameSettingsService with mocked dependencies"""
    return GameSettingsService(db=mock_postgres_db, redis=mock_redis)


@pytest.fixture
def sample_catalog():
    """Mock CATALOG with sample items for testing"""
    from game_internals.core.schemas.items import Gear, WeaponOnly

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
