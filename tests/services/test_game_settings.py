import pytest
from game_internals.core.schemas.game_settings import GameSettings


# ── fixtures ────────────────────────────────────────────────────────────────





# ── get_settings ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_settings_cache_miss_returns_defaults(service, player, mock_redis):
    """cache miss with empty preferences returns default settings"""
    mock_redis.get.return_value = None
    player.preferences = {}

    settings = await service.get_settings(player)

    assert settings.current_language == "en"
    mock_redis.set.assert_called_once()  # should have cached the result


@pytest.mark.asyncio
async def test_get_settings_cache_hit_skips_db(service, player, mock_redis):
    """cache hit returns immediately without touching preferences"""
    cached = GameSettings(current_language="fr")
    mock_redis.get.return_value = cached.model_dump_json()

    settings = await service.get_settings(player)

    assert settings.current_language == "fr"
    mock_redis.set.assert_not_called()  # no re-caching needed


@pytest.mark.asyncio
async def test_get_settings_cache_miss_populates_cache(service, player, mock_redis):
    """on cache miss, result should be written to redis"""
    mock_redis.get.return_value = None
    player.preferences = {"current_language": "fr"}

    await service.get_settings(player)

    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert f"settings:{player.id}" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_settings_loads_existing_preferences(service, player, mock_redis):
    """player with existing preferences gets those back, not defaults"""
    mock_redis.get.return_value = None
    player.preferences = {"current_language": "fr"}

    settings = await service.get_settings(player)

    assert settings.current_language == "fr"


# ── update_settings ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_settings_writes_to_db(service, player, mock_db):
    """update should persist to postgres"""
    await service.update_settings(player, current_language="fr")

    mock_db.add.assert_called_once_with(player)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_settings_updates_cache(service, player, mock_redis):
    """update should refresh redis cache"""
    await service.update_settings(player, current_language="fr")

    mock_redis.set.assert_called()
    last_call = mock_redis.set.call_args_list[-1]
    assert f"settings:{player.id}" in last_call[0][0]


@pytest.mark.asyncio
async def test_update_settings_returns_updated_schema(service, player):
    """return value should reflect the update"""
    result = await service.update_settings(player, current_language="fr")

    assert result.current_language == "fr"


@pytest.mark.asyncio
async def test_update_settings_invalid_language_raises(service, player):
    """passing unsupported language should raise validation error"""
    with pytest.raises(Exception):
        await service.update_settings(player, current_language="de")


@pytest.mark.asyncio
async def test_update_settings_mutates_player_preferences(service, player):
    """player.preferences dict should be updated after call"""
    await service.update_settings(player, current_language="fr")

    assert player.preferences.get("current_language") == "fr"


# ── update_language ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_language_valid(service, player):
    """valid language update should succeed and return updated settings"""
    result = await service.update_language(player, "fr")

    assert result.current_language == "fr"


@pytest.mark.asyncio
async def test_update_language_invalid_raises(service, player):
    """invalid language should raise before hitting db"""
    with pytest.raises(Exception):
        await service.update_language(player, "de")  # type: ignore


@pytest.mark.asyncio
async def test_update_language_persists(service, player, mock_db):
    """language change should be committed to db"""
    await service.update_language(player, "fr")

    mock_db.commit.assert_called_once()
