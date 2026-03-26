import pytest

from backend.services.game_settings import GameSettingsService


@pytest.fixture
def mock_mymemory_api_response():
    """Mock response from MyMemory translation API"""
    from unittest.mock import MagicMock

    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {
        "responseData": {"translatedText": "Bonjour le monde", "match": 1.0},
        "responseStatus": 200,
    }
    return response


@pytest.fixture
def game_settings_service(mock_postgres_db, mock_redis):
    """GameSettingsService with mocked dependencies"""
    return GameSettingsService(db=mock_postgres_db, redis=mock_redis)
