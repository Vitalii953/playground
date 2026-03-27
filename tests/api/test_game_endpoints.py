"""
Integration tests for game API endpoints
Tests the full game flow without polluting the main database
"""

import asyncio
import os
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.api.main import app
from backend.core.database import get_db
from backend.core.redis import get_redis
from backend.models.players import Base
from backend.models.players import Player as DBPlayer

# Test database URL (use env vars + container service host by default)
# In Docker Compose, Postgres is reachable at host `db`.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_HOST', 'db')}:5432/{os.getenv('POSTGRES_DB', 'sandbox_db')}",
)


@pytest_asyncio.fixture(scope="session")  # type: ignore
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_player(test_engine):
    """Create a test player in the database"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        player = DBPlayer(
            id=uuid4(),
            gold=100,
            keys=0,
            current_floor=0,
            preferences={},
            equipment={},
        )
        session.add(player)
        await session.commit()
        await session.refresh(player)

        yield player
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine, test_redis):
    """Create test HTTP client with dependency overrides"""

    async def override_get_db():
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        async_session_local = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_local() as session:
            yield session
        await engine.dispose()

    async def override_get_redis():
        yield test_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_redis():
    """Get Redis client for tests"""
    redis = await get_redis()

    # Clear test keys before each test
    async for key in redis.scan_iter(match="game_session:*"):
        await redis.delete(key)
    async for key in redis.scan_iter(match="session:*"):
        await redis.delete(key)

    yield redis

    # Cleanup after test
    async for key in redis.scan_iter(match="game_session:*"):
        await redis.delete(key)
    async for key in redis.scan_iter(match="session:*"):
        await redis.delete(key)

    await redis.close()


async def create_test_player(client, language: str = "en"):
    """Helper to create a player via API endpoint"""
    response = await client.post(
        "/api/v1/game/create-player", json={"language": language}
    )
    assert response.status_code == 200
    data = response.json()
    return data["player_id"]


# Tests
@pytest.mark.asyncio
async def test_create_player(client):
    """Test creating a new player"""
    response = await client.post("/api/v1/game/create-player", json={"language": "en"})

    assert response.status_code == 200
    data = response.json()

    assert "player_id" in data
    assert "message" in data
    assert data["message"] == "Player created successfully"
    assert "backend_events" in data

    # Verify backend events
    events = data["backend_events"]
    assert any(e["type"] == "db_write" for e in events)


@pytest.mark.asyncio
async def test_create_player_with_language(client):
    """Test creating a player with specific language preference"""
    response = await client.post("/api/v1/game/create-player", json={"language": "es"})

    assert response.status_code == 200
    data = response.json()
    assert "player_id" in data


@pytest.mark.asyncio
async def test_start_game(client, test_player):
    """Test starting a new game session"""
    response = await client.post(
        "/api/v1/game/start", json={"player_id": str(test_player.id), "language": "en"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "session_token" in data
    assert "player_state" in data
    assert "backend_events" in data

    # Verify player state
    player_state = data["player_state"]
    assert player_state["coins"] == 100
    assert player_state["floor"] == 0

    # Verify backend events
    events = data["backend_events"]
    assert any(e["type"] == "db_read" for e in events)
    assert any(e["type"] == "cache_write" for e in events)
    assert any(e["type"] == "session_create" for e in events)

    return data["session_token"]


@pytest.mark.asyncio
async def test_game_turn(client, test_player):
    """Test executing a game turn"""
    # Start game first
    start_response = await client.post(
        "/api/v1/game/start", json={"player_id": str(test_player.id), "language": "en"}
    )
    session_token = start_response.json()["session_token"]

    # Execute turn
    response = await client.post(
        "/api/v1/game/turn", json={"session_token": session_token, "language": "en"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "event" in data
    assert "player_state" in data
    assert "backend_events" in data

    # Verify backend events show cache usage
    events = data["backend_events"]
    assert any(e["type"] == "cache_hit" for e in events)
    assert any(e["type"] == "event_trigger" for e in events)
    assert any(e["type"] == "cache_write" for e in events)

    # Verify no DB access during turn
    assert not any(e["type"] == "db_read" for e in events)
    assert not any(e["type"] == "db_write" for e in events)


@pytest.mark.asyncio
async def test_resolve_action(client, test_player):
    """Test resolving a pending action (item equip)"""
    # Start game
    start_response = await client.post(
        "/api/v1/game/start", json={"player_id": str(test_player.id), "language": "en"}
    )
    session_token = start_response.json()["session_token"]

    # Execute turns until we get an item offer
    max_attempts = 20
    item_event = None

    for _ in range(max_attempts):
        turn_response = await client.post(
            "/api/v1/game/turn", json={"session_token": session_token, "language": "en"}
        )

        event = turn_response.json()["event"]
        if event and event.get("needs_input") and event.get("type") == "random_item":
            item_event = event
            break

    if not item_event:
        pytest.skip("No item event occurred in 20 turns")

    # Resolve action - equip the item
    response = await client.post(
        "/api/v1/game/resolve",
        json={
            "session_token": session_token,
            "language": "en",
            "event_type": item_event["type"],
            "event_value": item_event["value"],
            "decision": "equip",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "result_message" in data
    assert "player_state" in data

    # Verify item was equipped
    player_state = data["player_state"]
    equipment = player_state["equipment"]
    assert any(item is not None for item in equipment.values())


@pytest.mark.asyncio
async def test_end_game(client, test_player):
    """Test ending a game session"""
    # Start game
    start_response = await client.post(
        "/api/v1/game/start", json={"player_id": str(test_player.id), "language": "en"}
    )
    session_token = start_response.json()["session_token"]

    # Play a few turns
    for _ in range(3):
        await client.post(
            "/api/v1/game/turn", json={"session_token": session_token, "language": "en"}
        )

    # End game
    response = await client.post(
        "/api/v1/game/end", json={"session_token": session_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Game ended successfully"
    assert "final_state" in data
    assert "backend_events" in data

    # Verify DB write occurred
    events = data["backend_events"]
    assert any(e["type"] == "db_write" for e in events)
    assert any(e["type"] == "session_end" for e in events)


@pytest.mark.asyncio
async def test_resume_game(client, test_player):
    """Test resuming an existing game session"""
    # Start game
    start_response = await client.post(
        "/api/v1/game/start", json={"player_id": str(test_player.id), "language": "en"}
    )
    session_token = start_response.json()["session_token"]

    # Play a turn
    await client.post(
        "/api/v1/game/turn", json={"session_token": session_token, "language": "en"}
    )

    # Resume game
    response = await client.post(
        "/api/v1/game/resume", json={"session_token": session_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert "player_state" in data
    assert "session_info" in data
    assert "backend_events" in data

    # Verify session info
    session_info = data["session_info"]
    assert "turn_count" in session_info
    assert session_info["turn_count"] >= 1


@pytest.mark.asyncio
async def test_invalid_session(client):
    """Test that invalid session tokens are rejected"""
    response = await client.post(
        "/api/v1/game/turn",
        json={"session_token": "invalid_token_12345", "language": "en"},
    )

    assert response.status_code == 404
    assert "Invalid or expired session" in response.json()["detail"]


@pytest.mark.asyncio
async def test_start_without_player(client):
    """Test that starting game without creating player first fails"""
    fake_player_id = str(uuid4())
    response = await client.post(
        "/api/v1/game/start", json={"player_id": fake_player_id, "language": "en"}
    )

    assert response.status_code == 404
    assert "Player not found" in response.json()["detail"]
    assert "create-player" in response.json()["detail"]


@pytest.mark.asyncio
async def test_full_game_flow(client, test_player):
    """Test complete game flow from start to end"""
    # 1. Start game
    start_response = await client.post(
        "/api/v1/game/start", json={"player_id": str(test_player.id), "language": "en"}
    )
    assert start_response.status_code == 200
    session_token = start_response.json()["session_token"]

    # 2. Play multiple turns
    for i in range(10):
        turn_response = await client.post(
            "/api/v1/game/turn", json={"session_token": session_token, "language": "en"}
        )
        assert turn_response.status_code == 200

        event = turn_response.json()["event"]

        # If item offered, resolve it
        if event and event.get("needs_input"):
            resolve_response = await client.post(
                "/api/v1/game/resolve",
                json={
                    "session_token": session_token,
                    "language": "en",
                    "event_type": event["type"],
                    "event_value": event["value"],
                    "decision": "equip" if i % 2 == 0 else "reject",
                },
            )
            assert resolve_response.status_code == 200

    # 3. Resume game (simulate browser close/reopen)
    resume_response = await client.post(
        "/api/v1/game/resume", json={"session_token": session_token}
    )
    assert resume_response.status_code == 200

    # 4. End game
    end_response = await client.post(
        "/api/v1/game/end", json={"session_token": session_token}
    )
    assert end_response.status_code == 200

    # 5. Verify session is cleared (can't resume after end)
    resume_after_end = await client.post(
        "/api/v1/game/resume", json={"session_token": session_token}
    )
    assert resume_after_end.status_code == 404


@pytest.mark.asyncio
async def test_full_flow_with_create_player(client):
    """Test complete flow starting with player creation"""
    # 1. Create player
    player_id = await create_test_player(client, language="en")

    # 2. Start game
    start_response = await client.post(
        "/api/v1/game/start", json={"player_id": player_id, "language": "en"}
    )
    assert start_response.status_code == 200
    session_token = start_response.json()["session_token"]

    # 3. Play a few turns
    for _ in range(5):
        turn_response = await client.post(
            "/api/v1/game/turn", json={"session_token": session_token, "language": "en"}
        )
        assert turn_response.status_code == 200

        event = turn_response.json()["event"]
        if event and event.get("needs_input"):
            await client.post(
                "/api/v1/game/resolve",
                json={
                    "session_token": session_token,
                    "language": "en",
                    "event_type": event["type"],
                    "event_value": event["value"],
                    "decision": "equip",
                },
            )

    # 4. End game
    end_response = await client.post(
        "/api/v1/game/end", json={"session_token": session_token}
    )
    assert end_response.status_code == 200
