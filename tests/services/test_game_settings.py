import pytest

from game_internals.core.schemas.game_settings import GameSettings

# ── fixtures ────────────────────────────────────────────────────────────────


# ── get_settings ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_settings_cache_miss_returns_defaults(
    game_settings_service, player, mock_redis
):
    """cache miss with empty preferences returns default settings"""
    mock_redis.get.return_value = None
    player.preferences = {}

    settings = await game_settings_service.get_settings(player)

    assert settings.current_language == "en"
    mock_redis.set.assert_called_once()  # should have cached the result


@pytest.mark.asyncio
async def test_get_settings_cache_hit_skips_db(
    game_settings_service, player, mock_redis
):
    """cache hit returns immediately without touching preferences"""
    cached = GameSettings(current_language="fr")
    mock_redis.get.return_value = cached.model_dump_json()

    settings = await game_settings_service.get_settings(player)

    assert settings.current_language == "fr"
    mock_redis.set.assert_not_called()  # no re-caching needed


@pytest.mark.asyncio
async def test_get_settings_cache_miss_populates_cache(
    game_settings_service, player, mock_redis
):
    """on cache miss, result should be written to redis"""
    mock_redis.get.return_value = None
    player.preferences = {"current_language": "fr"}

    await game_settings_service.get_settings(player)

    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert f"settings:{player.id}" in call_args[0][0]


@pytest.mark.asyncio
async def test_get_settings_loads_existing_preferences(
    game_settings_service, player, mock_redis
):
    """player with existing preferences gets those back, not defaults"""
    mock_redis.get.return_value = None
    player.preferences = {"current_language": "fr"}

    settings = await game_settings_service.get_settings(player)

    assert settings.current_language == "fr"


# ── update_settings ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_settings_writes_to_db(
    game_settings_service, player, mock_postgres_db
):
    """update should persist to postgres"""
    await game_settings_service.update_settings(player, current_language="fr")

    mock_postgres_db.add.assert_called_once_with(player)
    mock_postgres_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_settings_updates_cache(game_settings_service, player, mock_redis):
    """update should refresh redis cache"""
    await game_settings_service.update_settings(player, current_language="fr")

    mock_redis.set.assert_called()
    last_call = mock_redis.set.call_args_list[-1]
    assert f"settings:{player.id}" in last_call[0][0]


@pytest.mark.asyncio
async def test_update_settings_returns_updated_schema(game_settings_service, player):
    """return value should reflect the update"""
    result = await game_settings_service.update_settings(player, current_language="fr")

    assert result.current_language == "fr"


@pytest.mark.asyncio
async def test_update_settings_invalid_language_raises(game_settings_service, player):
    """passing unsupported language should raise validation error"""
    with pytest.raises(Exception):
        await game_settings_service.update_settings(player, current_language="de")


@pytest.mark.asyncio
async def test_update_settings_mutates_player_preferences(
    game_settings_service, player
):
    """player.preferences dict should be updated after call"""
    await game_settings_service.update_settings(player, current_language="fr")

    assert player.preferences.get("current_language") == "fr"


# ── update_language ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_language_valid(game_settings_service, player):
    """valid language update should succeed and return updated settings"""
    result = await game_settings_service.update_language(player, "fr")

    assert result.current_language == "fr"


@pytest.mark.asyncio
async def test_update_language_invalid_raises(game_settings_service, player):
    """invalid language should raise before hitting db"""
    with pytest.raises(Exception):
        await game_settings_service.update_language(player, "de")  # type: ignore


@pytest.mark.asyncio
async def test_update_language_persists(
    game_settings_service, player, mock_postgres_db
):
    """language change should be committed to db"""
    await game_settings_service.update_language(player, "fr")

    mock_postgres_db.commit.assert_called_once()
