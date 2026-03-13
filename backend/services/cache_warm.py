"""
This creates cache as soon as the app launches with 1 async function
its low-level too, so as everywhere else, i'll handle it
on the most abstracted layer. Not here.
"""

from redis.asyncio import Redis
from backend.services.translator.translation_service import translate
from game_internals.core.schemas.game_settings import languages
from game_internals.core.phrases import PHRASES
from typing import get_args
import logging
import asyncio


logger = logging.getLogger(__name__)


async def warm_cache(collection: list, redis: Redis):
    """
    the collection is all the phrases and whatnot...
    """
    supported_languages = get_args(languages)

    # TODO: filter by presence of brackets "{}"

    tasks = [
        translate(text, lang, redis)
        for text in collection
        for lang in supported_languages
    ]
    res = await asyncio.gather(*tasks, return_exceptions=True)

    for idx, result in enumerate(res):
        if isinstance(result, Exception):
            logger.error(
                "Error caching translation for '%s': %s",
                collection[idx // len(supported_languages)],
                result,
            )
        else:
            logger.info(
                "Successfully cached translation for '%s'",
                collection[idx // len(supported_languages)],
            )
