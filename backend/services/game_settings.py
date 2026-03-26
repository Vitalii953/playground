from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from game_internals.core.schemas.game_settings import GameSettings, languages
from backend.models.players import Player
import logging


logger = logging.getLogger(__name__)


class GameSettingsService:

    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis

    async def get_settings(self, player: Player) -> GameSettings:
        """get player settings, cache if needed"""

        cached = await self.redis.get(f"settings:{player.id}")
        if cached:
            return GameSettings.model_validate_json(cached)

        # validate settings
        settings = GameSettings.model_validate(
            player.preferences or {}
        )  # getting brackets would mean a bug
        if settings == {}:
            logger.warning("Expected settings, got an empty dictionary")

        await self.redis.set(
            f"settings:{player.id}", settings.model_dump_json(), ex=7200
        )
        logger.info("Settings cached for %s", player.id)
        return settings

    async def update_settings(self, player: Player, **kwargs) -> GameSettings:
        """update settings by passing only required fields"""

        current_settings = await self.get_settings(player)
        updated_settings = GameSettings.model_validate(
            current_settings.model_dump() | kwargs
        )  # merges and validates
        player.preferences = updated_settings.model_dump()

        self.db.add(player)
        await self.db.commit()
        logger.info("Settings updated for %s", player.id)

        await self.redis.set(
            f"settings:{player.id}", updated_settings.model_dump_json(), ex=7200
        )
        logger.info("Settings cached for %s", player.id)
        return updated_settings

    # high level function
    async def update_language(self, player: Player, language: languages):
        """Abstraction built upon update_settings()"""

        try:
            updated = await self.update_settings(player, current_language=language)

        except Exception as e:
            logger.error("Exception occured: %s", e)
            raise

        return updated
