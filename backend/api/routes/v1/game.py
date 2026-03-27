"""
Game API routes for turn-based gameplay
Thin route handlers that delegate to service layer
"""

import logging
import time
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.redis import get_redis
from backend.models.players import Player as DBPlayer
from backend.services.player_cache import (
    get_cached_player,
    cache_player,
    clear_cached_player,
)
from backend.services.game_session import (
    create_session,
    get_session,
    update_session_activity,
    delete_session,
)
from backend.services.auto_save import save_player_to_db
from game_internals.core.gameplay.entities.player import Player as GamePlayer
from game_internals.core.gameplay.turns_logic.helper_loops import (
    go_one_step,
    resolve_pending_action,
)
from game_internals.core.schemas.game_settings import languages

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/game", tags=["game"])


# Request/Response schemas
class CreatePlayerRequest(BaseModel):
    name: str | None = None
    language: languages = "en"


class CreatePlayerResponse(BaseModel):
    player_id: UUID
    message: str
    backend_events: list[BackendEvent]


class StartGameRequest(BaseModel):
    player_id: UUID
    language: languages


class TurnRequest(BaseModel):
    session_token: str
    language: languages


class ResolveRequest(BaseModel):
    session_token: str
    language: languages
    event_type: str
    event_value: dict
    decision: str


class EndGameRequest(BaseModel):
    session_token: str


class ResumeRequest(BaseModel):
    session_token: str


class BackendEvent(BaseModel):
    type: str
    message: str
    duration_ms: float | None = None
    timestamp: str


class PlayerStateResponse(BaseModel):
    hp: int | float
    max_hp: int | float
    attack: int | float
    speed: int | float
    coins: int
    floor: int
    equipment: dict


class StartGameResponse(BaseModel):
    session_token: str
    player_state: PlayerStateResponse
    backend_events: list[BackendEvent]


class TurnResponse(BaseModel):
    event: dict | None
    player_state: PlayerStateResponse
    backend_events: list[BackendEvent]


class ResolveResponse(BaseModel):
    result_message: str
    player_state: PlayerStateResponse
    backend_events: list[BackendEvent]


class EndGameResponse(BaseModel):
    message: str
    final_state: PlayerStateResponse
    backend_events: list[BackendEvent]


class ResumeResponse(BaseModel):
    player_state: PlayerStateResponse
    session_info: dict
    backend_events: list[BackendEvent]


# Helper functions
def game_player_to_state(player: GamePlayer) -> PlayerStateResponse:
    """Convert GamePlayer to API response format"""
    return PlayerStateResponse(
        hp=player.current_hp,
        max_hp=player.total_hp,
        attack=player.current_attack,
        speed=player.current_speed,
        coins=player.coins,
        floor=player.floor,
        equipment={
            slot: item.model_dump() if item else None
            for slot, item in player.equipped.items()
        },
    )


def create_backend_event(event_type: str, message: str, duration_ms: float | None = None) -> BackendEvent:
    """Helper to create backend event with timestamp"""
    return BackendEvent(
        type=event_type,
        message=message,
        duration_ms=duration_ms,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
    )


# Routes
@router.post("/create-player", response_model=CreatePlayerResponse)
async def create_player(
    request: CreatePlayerRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new player in the database"""
    backend_events = []

    try:
        # Create new player
        db_start = time.time()
        new_player = DBPlayer(
            gold=0,
            keys=0,
            current_floor=0,
            preferences={"language": request.language},
            equipment={}
        )
        db.add(new_player)
        await db.commit()
        await db.refresh(new_player)

        backend_events.append(
            create_backend_event(
                "db_write",
                "Created new player in database",
                round((time.time() - db_start) * 1000, 2),
            )
        )

        return CreatePlayerResponse(
            player_id=new_player.id,
            message="Player created successfully",
            backend_events=backend_events,
        )

    except Exception as e:
        logger.error(f"Error in create_player: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start", response_model=StartGameResponse)
async def start_game(
    request: StartGameRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Start a new game session"""
    backend_events = []

    try:
        # Load player from DB
        db_start = time.time()
        result = await db.execute(
            select(DBPlayer).where(DBPlayer.id == request.player_id)
        )
        db_player = result.scalar_one_or_none()

        if not db_player:
            raise HTTPException(status_code=404, detail="Player not found. Call /create-player first.")

        backend_events.append(
            create_backend_event(
                "db_read",
                "Loaded player from database",
                round((time.time() - db_start) * 1000, 2),
            )
        )

        # Create game player instance
        game_player = GamePlayer(
            name=f"Player_{request.player_id}",
            hp=100,
            attack=10,
            speed=10,
        )
        game_player.coins = db_player.gold
        game_player.floor = db_player.current_floor

        # Cache in Redis
        cache_start = time.time()
        await cache_player(request.player_id, game_player, redis)
        backend_events.append(
            create_backend_event(
                "cache_write",
                "Player cached in Redis",
                round((time.time() - cache_start) * 1000, 2),
            )
        )

        # Create session
        session_token = await create_session(request.player_id, redis)
        backend_events.append(create_backend_event("session_create", "Game session created", 0.5))

        return StartGameResponse(
            session_token=session_token,
            player_state=game_player_to_state(game_player),
            backend_events=backend_events,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in start_game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turn", response_model=TurnResponse)
async def game_turn(
    request: TurnRequest,
    redis: Redis = Depends(get_redis),
):
    """Execute one game turn"""
    backend_events = []

    try:
        # Validate session
        session = await get_session(request.session_token, redis)
        if not session:
            raise HTTPException(status_code=404, detail="Invalid or expired session")

        player_id = UUID(session["player_id"])

        # Load player from cache
        cache_start = time.time()
        game_player = await get_cached_player(player_id, redis)

        if not game_player:
            raise HTTPException(
                status_code=404,
                detail="Player not found in cache. Session may have expired."
            )

        backend_events.append(
            create_backend_event(
                "cache_hit",
                "Player loaded from Redis cache",
                round((time.time() - cache_start) * 1000, 2),
            )
        )

        # Execute one game step
        event_start = time.time()
        event_result = await go_one_step(game_player, request.language, redis)

        event_type = event_result.get('type', 'unknown') if event_result else 'none'
        backend_events.append(
            create_backend_event(
                "event_trigger",
                f"Event: {event_type}",
                round((time.time() - event_start) * 1000, 2),
            )
        )

        # Check if player died
        if not game_player.is_alive():
            backend_events.append(
                create_backend_event("player_death", "Player died - game over")
            )

        # Update cache
        cache_write_start = time.time()
        await cache_player(player_id, game_player, redis)
        backend_events.append(
            create_backend_event(
                "cache_write",
                "Player state updated in cache",
                round((time.time() - cache_write_start) * 1000, 2),
            )
        )

        # Update session activity
        await update_session_activity(request.session_token, redis, increment_turn=True)

        return TurnResponse(
            event=event_result,
            player_state=game_player_to_state(game_player),
            backend_events=backend_events,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in game_turn: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve", response_model=ResolveResponse)
async def resolve_action(
    request: ResolveRequest,
    redis: Redis = Depends(get_redis),
):
    """Resolve a pending action that required player input"""
    backend_events = []

    try:
        # Validate session
        session = await get_session(request.session_token, redis)
        if not session:
            raise HTTPException(status_code=404, detail="Invalid or expired session")

        player_id = UUID(session["player_id"])

        # Load player from cache
        cache_start = time.time()
        game_player = await get_cached_player(player_id, redis)

        if not game_player:
            raise HTTPException(status_code=404, detail="Player not found in cache")

        backend_events.append(
            create_backend_event(
                "cache_hit",
                "Player loaded from Redis cache",
                round((time.time() - cache_start) * 1000, 2),
            )
        )

        # Reconstruct event response
        event_response = {
            "type": request.event_type,
            "value": request.event_value,
            "needs_input": True,
            "decision": request.decision,
        }

        # Resolve action
        resolve_start = time.time()
        result_message = await resolve_pending_action(
            event_response, game_player, request.language, redis
        )
        backend_events.append(
            create_backend_event(
                "action_resolved",
                f"Resolved: {request.decision}",
                round((time.time() - resolve_start) * 1000, 2),
            )
        )

        # Update cache
        cache_write_start = time.time()
        await cache_player(player_id, game_player, redis)
        backend_events.append(
            create_backend_event(
                "cache_write",
                "Player state updated in cache",
                round((time.time() - cache_write_start) * 1000, 2),
            )
        )

        # Update session activity
        await update_session_activity(request.session_token, redis)

        return ResolveResponse(
            result_message=result_message or "Action resolved",
            player_state=game_player_to_state(game_player),
            backend_events=backend_events,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resolve_action: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end", response_model=EndGameResponse)
async def end_game(
    request: EndGameRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """End game session and save to database"""
    backend_events = []

    try:
        # Validate session
        session = await get_session(request.session_token, redis)
        if not session:
            raise HTTPException(status_code=404, detail="Invalid or expired session")

        player_id = UUID(session["player_id"])

        # Load player from cache
        cache_start = time.time()
        game_player = await get_cached_player(player_id, redis)

        if not game_player:
            raise HTTPException(status_code=404, detail="Player not found in cache")

        backend_events.append(
            create_backend_event(
                "cache_hit",
                "Player loaded from Redis cache",
                round((time.time() - cache_start) * 1000, 2),
            )
        )

        # Save to DB
        db_start = time.time()
        await save_player_to_db(player_id, game_player, db)
        backend_events.append(
            create_backend_event(
                "db_write",
                "Final player state saved to database",
                round((time.time() - db_start) * 1000, 2),
            )
        )

        # Clear cache and session
        await clear_cached_player(player_id, redis)
        await delete_session(request.session_token, redis)
        backend_events.append(
            create_backend_event("session_end", "Game session ended and cleared", 0.1)
        )

        return EndGameResponse(
            message="Game ended successfully",
            final_state=game_player_to_state(game_player),
            backend_events=backend_events,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in end_game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=ResumeResponse)
async def resume_game(
    request: ResumeRequest,
    redis: Redis = Depends(get_redis),
):
    """Resume an existing game session"""
    backend_events = []

    try:
        # Validate session
        session = await get_session(request.session_token, redis)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired. Please start a new game."
            )

        player_id = UUID(session["player_id"])

        # Load player from cache
        cache_start = time.time()
        game_player = await get_cached_player(player_id, redis)

        if not game_player:
            raise HTTPException(
                status_code=404,
                detail="Player cache expired. Please start a new game."
            )

        backend_events.append(
            create_backend_event(
                "cache_hit",
                "Player loaded from Redis cache",
                round((time.time() - cache_start) * 1000, 2),
            )
        )

        # Calculate session info
        session_info = {
            "turn_count": session.get("turn_count", 0),
            "started_at": session.get("started_at"),
            "idle_time_seconds": round(time.time() - session.get("last_turn_at", time.time())),
        }

        return ResumeResponse(
            player_state=game_player_to_state(game_player),
            session_info=session_info,
            backend_events=backend_events,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resume_game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
