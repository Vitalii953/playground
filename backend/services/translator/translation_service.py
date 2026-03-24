"""
this is another low-level module. I will be calling it just once during initialization ig
"""

import httpx
from backend.services.translator.config import get_settings
from redis.asyncio import Redis
from game_internals.core.schemas.game_settings import languages
import logging


logger = logging.getLogger(__name__)
settings = get_settings()  # for building URL


BASE_URL = settings.base_url
email = settings.personal_email
cache_time = settings.cache_time


async def translate(text: str, to_language: languages, redis: Redis) -> str:
    """
    this ALWAYS translates from English since the app assumes it as the default language.
    therefore, this function is also tailored to translate from english only
    DOES NOT CACHE ANYTHING - warm_cache handles this
    """
    
    if to_language == "en":
        return text

    cache = f"translation:{to_language}:{hash(text)}"  # acts as key:value because it is

    cached = await redis.get(cache)
    if cached:
        return cached

    # mymemory api is url-based, it parses, therefore i build URL dynamically
    params = {"q": text, "langpair": f"en|{to_language}", "de": email}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(str(BASE_URL), params=params)
            r.raise_for_status()  # fails loudly if goes south
    except httpx.HTTPStatusError as e:
        logger.error("Mymemory responded with 4xx or 5xx: %s", e)
        raise
    except httpx.RequestError as e:  # generic httpx error
        logger.error("Mymemory error while requesting data: %s", e)
        raise

    result = r.json()["responseData"]["translatedText"]

    return result
