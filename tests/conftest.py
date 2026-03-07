import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
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
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def service(mock_db, mock_redis):
    return GameSettingsService(db=mock_db, redis=mock_redis)
