"""
Auto-save background service
Periodically saves idle game sessions to database
"""

import asyncio
import logging
import time
from uuid import UUID
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.players import Player as DBPlayer
from backend.services.player_cache import get_cached_player, game_player_to_dict
from backend.services.game_session import get_session, update_session

logger = logging.getLogger(__name__)


async def save_player_to_db(player_id: UUID, game_player, db: AsyncSession):
    """Save game player state to database"""
    result = await db.execute(
        select(DBPlayer).where(DBPlayer.id == player_id)
    )
    db_player = result.scalar_one_or_none()

    if not db_player:
        logger.warning(f"Player {player_id} not found in DB during auto-save")
        return

    db_player.gold = game_player.coins
    db_player.current_floor = game_player.floor
    db_player.equipment = game_player_to_dict(game_player)["equipped"]

    await db.commit()


async def check_and_save_sessions(redis: Redis, db_factory):
    """Check all sessions and save stale ones"""
    pattern = "session:*"
    saved_count = 0

    async for key in redis.scan_iter(match=pattern):
        try:
            session_token = key.removeprefix(b"session:").decode()
            session = await get_session(session_token, redis)

            if not session:
                continue

            last_turn = session.get("last_turn_at", 0)
            last_save = session.get("last_save_at", 0)
            idle_time = time.time() - last_turn

            # Only save if idle > 5 minutes AND not saved recently
            if idle_time > 300 and (time.time() - last_save) > 300:
                player_id = UUID(session["player_id"])
                game_player = await get_cached_player(player_id, redis)

                if not game_player:
                    continue

                # Save to DB
                async with db_factory() as db:
                    await save_player_to_db(player_id, game_player, db)

                logger.info(f"Auto-saved player {player_id} after {idle_time:.0f}s idle")

                # Update session to mark as saved
                session["last_save_at"] = time.time()
                await update_session(session_token, session, redis)
                saved_count += 1

        except Exception as e:
            logger.error(f"Error auto-saving session: {e}", exc_info=True)

    return saved_count


async def auto_save_stale_sessions(redis: Redis, db_factory, shutdown_event: asyncio.Event):
    """
    Background task that periodically saves idle sessions.
    Runs immediately on startup, then every 60 seconds.
    Handles graceful shutdown via shutdown_event.
    """
    logger.info("Auto-save background task started")

    try:
        # Run immediately on startup
        saved = await check_and_save_sessions(redis, db_factory)
        if saved > 0:
            logger.info(f"Startup auto-save: saved {saved} sessions")

        # Then run every 60 seconds
        while not shutdown_event.is_set():
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=60.0)
                break  # Shutdown requested
            except asyncio.TimeoutError:
                # Timeout means no shutdown, continue with save
                saved = await check_and_save_sessions(redis, db_factory)
                if saved > 0:
                    logger.info(f"Auto-saved {saved} sessions")

    except asyncio.CancelledError:
        logger.info("Auto-save task cancelled, performing final save...")
        # Final save before shutdown
        saved = await check_and_save_sessions(redis, db_factory)
        logger.info(f"Final auto-save: saved {saved} sessions")
        raise

    logger.info("Auto-save background task stopped")
