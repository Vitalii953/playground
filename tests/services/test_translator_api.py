from unittest.mock import AsyncMock, patch

import pytest

from backend.api.main import api_translate


@pytest.mark.asyncio
async def test_api_translate_uses_translator_and_closes_redis(mock_redis):
    mock_redis.close = AsyncMock()

    with patch(
        "backend.api.main.get_redis", AsyncMock(return_value=mock_redis)
    ) as mock_get_redis:
        with patch(
            "backend.api.main.translate", AsyncMock(return_value="Bonjour")
        ) as mock_translate:
            result = await api_translate("Hello", "fr")

    assert result == {"text": "Hello", "to_language": "fr", "translated": "Bonjour"}
    mock_get_redis.assert_called_once()
    mock_translate.assert_called_once_with("Hello", "fr", mock_redis)
    mock_redis.close.assert_awaited_once()
