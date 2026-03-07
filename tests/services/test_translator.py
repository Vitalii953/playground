from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend.services.translator.translation_service import translate

# ── cache hit ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_translate_cache_hit_returns_cached(mock_redis):
    """cache hit should return immediately without calling the API"""
    mock_redis.get.return_value = "Bonjour le monde"

    result = await translate("Hello world", "fr", mock_redis)

    assert result == "Bonjour le monde"
    mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_translate_cache_hit_skips_api(mock_redis):
    """cache hit should never reach the external API"""
    mock_redis.get.return_value = "Bonjour"

    with patch("httpx.AsyncClient") as mock_client:
        await translate("Hello", "fr", mock_redis)
        mock_client.assert_not_called()


# ── cache miss ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_translate_cache_miss_calls_api(mock_redis, mock_mymemory_api_response):
    """cache miss should call the MyMemory API"""
    mock_redis.get.return_value = None

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_mymemory_api_response
        )

        result = await translate("Hello world", "fr", mock_redis)

    assert result == "Bonjour le monde"


@pytest.mark.asyncio
async def test_translate_cache_miss_populates_cache(
    mock_redis, mock_mymemory_api_response
):
    """successful translation should be written to redis"""
    mock_redis.get.return_value = None

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_mymemory_api_response
        )

        await translate("Hello world", "fr", mock_redis)

    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert call_args.kwargs["ex"] == 36_000


@pytest.mark.asyncio
async def test_translate_cache_key_includes_language_and_text(
    mock_redis, mock_mymemory_api_response
):
    """different languages should produce different cache keys"""
    mock_redis.get.return_value = None

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_mymemory_api_response
        )

        await translate("Hello", "fr", mock_redis)
        await translate("Hello", "fr", mock_redis)

    # same text + language = same cache key = set called twice with same key
    first_key = mock_redis.set.call_args_list[0][0][0]
    second_key = mock_redis.set.call_args_list[1][0][0]
    assert first_key == second_key
    assert "fr" in first_key


# ── error handling ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_translate_http_status_error_raises(mock_redis):
    """API 4xx/5xx should raise and not cache anything"""
    mock_redis.get.return_value = None

    error_response = MagicMock()
    error_response.status_code = 429

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Too many requests", request=MagicMock(), response=error_response
            )
        )

        with pytest.raises(httpx.HTTPStatusError):
            await translate("Hello", "fr", mock_redis)

    mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_translate_request_error_raises(mock_redis):
    """network failure should raise and not cache anything"""
    mock_redis.get.return_value = None

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.RequestError("Connection failed", request=MagicMock())
        )

        with pytest.raises(httpx.RequestError):
            await translate("Hello", "fr", mock_redis)

    mock_redis.set.assert_not_called()


# ── params ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_translate_sends_correct_langpair(mock_redis, mock_mymemory_api_response):
    """langpair should always be en|{target_language}"""
    mock_redis.get.return_value = None

    with patch("httpx.AsyncClient") as mock_client:
        get_mock = AsyncMock(return_value=mock_mymemory_api_response)
        mock_client.return_value.__aenter__.return_value.get = get_mock

        await translate("Hello", "fr", mock_redis)

    call_params = get_mock.call_args.kwargs["params"]
    assert call_params["langpair"] == "en|fr"
    assert call_params["q"] == "Hello"
