import pytest

from backend.services.cache_warm import get_cacheable, warm_cache


def test_get_cacheable_excludes_dynamic_values():
    texts = {"a": "hello", "b": "hi {name}", "c": "goodbye"}
    got = get_cacheable(texts)

    assert "a" in got
    assert "c" in got
    assert "b" not in got


@pytest.mark.asyncio
async def test_warm_cache_calls_translate_for_every_cacheable_value(
    monkeypatch, mock_redis
):
    texts = {"a": "hello", "b": "hi {name}", "c": "goodbye"}

    translate_calls = []

    async def fake_translate(text, lang, redis):
        translate_calls.append((text, lang))
        return f"{text}-{lang}"

    monkeypatch.setattr("backend.services.cache_warm.translate", fake_translate)

    await warm_cache(texts, mock_redis)

    # only two cacheable keys, but for both languages
    assert len(translate_calls) == 2 * 2

    # ensure we translated expected strings
    assert ("hello", "en") in translate_calls
    assert ("goodbye", "fr") in translate_calls

    # verify warm_cache wrote translations into redis using the expected key format
    expected_keys = {
        f"translation:{lang}:{hash(text)}"
        for text in ("hello", "goodbye")
        for lang in ("en", "fr")
    }
    got_keys = {call.args[0] for call in mock_redis.set.call_args_list}
    assert expected_keys == got_keys
