"""
this is another low-level module. I will be calling it just once during initialization ig
"""
import httpx # type: ignore
from translator.config import get_settings  
from game_internals.core.schemas.game_settings import GameSettings, languages
from redis.asyncio import Redis


settings = get_settings()  # for building URL
BASE_URL = settings.base_url
email = settings.personal_email


async def translate(text: str, to_language: languages, redis: Redis) -> str:
    pass
#TODO: this is my todo priority rn