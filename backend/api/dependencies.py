"""
Session validation dependency
Provides FastAPI dependency for validating session tokens
"""

from uuid import UUID
from fastapi import HTTPException, Depends
from redis.asyncio import Redis

from backend.core.redis import get_redis
from backend.services.game_session import get_session


async def validate_session(session_token: str, redis: Redis = Depends(get_redis)) -> tuple[dict, UUID]:
    """
    Validate session token and return session data + player_id.
    Raises HTTPException if session is invalid.

    Usage in routes:
        session, player_id = Depends(validate_session)
    """
    session = await get_session(session_token, redis)

    if not session:
        raise HTTPException(status_code=404, detail="Invalid or expired session")

    player_id = UUID(session["player_id"])

    return session, player_id
