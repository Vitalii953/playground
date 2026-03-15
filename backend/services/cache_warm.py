"""
This creates cache as soon as the app launches with 1 async function
its low-level too, so as everywhere else, i'll handle it
on the most abstracted layer. Not here.
"""

from redis.asyncio import Redis
from backend.services.translator.translation_service import translate
from game_internals.core.schemas.game_settings import languages
from typing import get_args
import logging
import asyncio


logger = logging.getLogger(__name__)


def get_cacheable(texts: dict):
    """
    determines is fields contain dynammic values
    by looking for curly brackets
    """

    cacheable_fields = {}
    for key, value in texts.items():
        if "{" not in value or "}" not in value:  # if there are no dynamic values, it is cacheable
            cacheable_fields[key] = value
    return cacheable_fields

async def warm_cache(texts: dict, redis: Redis):
    """
    the collection is all the phrases and whatnot...
    this is how ALL cache is produced (so translation service uses this for cache lookups)
    """

    supported_languages = get_args(languages)

    cacheable_texts = get_cacheable(texts)
    cacheable_keys = list(cacheable_texts.keys())
    async def _translate_and_cache(key: str, text: str, lang: str) -> None:
        """Translate the text and store it in Redis under the translation key."""

        try:
            result = await translate(text, lang, redis)
            cache_key = f"translation:{lang}:{hash(text)}"
            await redis.set(cache_key, result)
            logger.info("Successfully cached translation for '%s'", key)
        except Exception as e:
            logger.error("Error caching translation for '%s': %s", key, e)

    tasks = [
        _translate_and_cache(key, cacheable_texts[key], lang)
        for key in cacheable_keys
        for lang in supported_languages
    ]
    await asyncio.gather(*tasks)
