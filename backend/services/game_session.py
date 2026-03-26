"""
Game session service
Handles session token management and metadata
"""

import json
import secrets
import time
from uuid import UUID
from redis.asyncio import Redis


async def create_session(player_id: UUID, redis: Redis, ttl: int = 7200) -> str:
    """
    Create a new game session.
    Returns session token.
    """
    session_token = secrets.token_urlsafe(32)
    session_data = {
        "player_id": str(player_id),
        "started_at": time.time(),
        "last_turn_at": time.time(),
        "last_save_at": time.time(),
        "turn_count": 0,
    }

    session_key = f"session:{session_token}"
    await redis.set(session_key, json.dumps(session_data), ex=ttl)

    return session_token


async def get_session(session_token: str, redis: Redis) -> dict | None:
    """Get session metadata from Redis"""
    session_key = f"session:{session_token}"
    cached = await redis.get(session_key)

    if not cached:
        return None

    return json.loads(cached)


async def update_session(session_token: str, session_data: dict, redis: Redis, ttl: int = 7200):
    """Update session metadata in Redis"""
    session_key = f"session:{session_token}"
    await redis.set(session_key, json.dumps(session_data), ex=ttl)


async def delete_session(session_token: str, redis: Redis):
    """Delete session from Redis"""
    session_key = f"session:{session_token}"
    await redis.delete(session_key)


async def update_session_activity(session_token: str, redis: Redis, increment_turn: bool = False):
    """
    Update session last_turn_at timestamp and optionally increment turn count.
    Returns updated session data or None if session not found.
    """
    session = await get_session(session_token, redis)

    if not session:
        return None

    session["last_turn_at"] = time.time()

    if increment_turn:
        session["turn_count"] = session.get("turn_count", 0) + 1

    await update_session(session_token, session, redis)
    return session
