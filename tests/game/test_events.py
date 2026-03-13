from unittest.mock import AsyncMock

import pytest

import game_internals.events as events


@pytest.mark.asyncio
async def test_offer_random_item_event_calls_translate_and_returns_item(
    monkeypatch, mock_redis
):
    class DummyItem:
        name = "Sword"

        def model_dump(self):
            return {"name": self.name}

    monkeypatch.setattr(events, "pick_random_item", lambda: DummyItem())
    translate_mock = AsyncMock(return_value="translated")
    monkeypatch.setattr(events, "translate", translate_mock)

    result = await events.offer_random_item_event("en", mock_redis)

    assert result["type"] == "random_item"
    assert result["value"] == {"name": "Sword"}
    assert result["report"] == "translated"
    assert result["needs_input"] is True

    # Should translate the formatted template string
    expected = "You found a Sword!"
    translate_mock.assert_awaited_once_with(expected, "en", mock_redis)


@pytest.mark.asyncio
async def test_floor_up_event_increments_floor_and_translates(
    monkeypatch, player, mock_redis
):
    translate_mock = AsyncMock(return_value="up")
    monkeypatch.setattr(events, "translate", translate_mock)

    assert player.floor == 0
    result = await events.floor_up_event(player, "en", mock_redis)

    assert player.floor == 1
    assert result["type"] == "floor_up"
    assert result["report"] == "up"


@pytest.mark.asyncio
async def test_add_coins_event_adds_coins_and_translates(
    monkeypatch, player, mock_redis
):
    # Force a predictable coin roll
    monkeypatch.setattr(events, "randint", lambda a, b: 10)
    translate_mock = AsyncMock(return_value="you got coins")
    monkeypatch.setattr(events, "translate", translate_mock)

    assert player.coins == 0
    result = await events.add_coins_event(player, "en", mock_redis)

    assert player.coins == 10
    assert result["type"] == "add_coins"
    assert result["value"] == 10
    assert result["report"] == "you got coins"


@pytest.mark.asyncio
async def test_heal_event_increases_hp(monkeypatch, player, mock_redis):
    # Prevent randomness so test is stable
    monkeypatch.setattr(events, "randint", lambda a, b: 10)
    translate_mock = AsyncMock(return_value="healed")
    monkeypatch.setattr(events, "translate", translate_mock)

    player.current_hp = 50
    result = await events.heal_event(player, "en", mock_redis)

    assert player.current_hp == 60
    assert result["type"] == "heal"
    assert result["value"] == 10
    assert result["report"] == "healed"


@pytest.mark.asyncio
async def test_poison_event_reduces_hp_and_reports(monkeypatch, player, mock_redis):
    # Always deal 2 damage each tick
    monkeypatch.setattr(events, "randint", lambda a, b: 2)
    translate_mock = AsyncMock(return_value="poisoned")
    monkeypatch.setattr(events, "translate", translate_mock)

    player.current_hp = 20
    result = await events.poison_event(player, "en", mock_redis)

    # 3 ticks of 2 damage each
    assert player.current_hp == 14
    assert result["type"] == "poison"
    assert result["value"] == 6
    assert result["report"] == "poisoned"


@pytest.mark.asyncio
async def test_summon_enemy_event_chooses_enemy_and_translates(monkeypatch, mock_redis):
    class DummyEnemy:
        name = "Goblin"

    monkeypatch.setattr(events, "ALL_ENEMIES", {"goblin": DummyEnemy})
    monkeypatch.setattr(events, "choices", lambda seq, k: ["goblin"])

    translate_mock = AsyncMock(return_value="enemy appeared")
    monkeypatch.setattr(events, "translate", translate_mock)

    result = await events.summon_enemy_event("en", mock_redis)

    assert result["type"] == "summon_enemy"
    assert isinstance(result["value"], DummyEnemy)
    assert result["report"] == "enemy appeared"

    translate_mock.assert_awaited_once()
