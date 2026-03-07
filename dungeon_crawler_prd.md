# DUNGEON CRAWLER — Backend Architecture Demo
### Product Requirements Document · v1.0 · 2026

---

## 1. Overview

This project is an educational backend-heavy demonstration built as a text-based dungeon crawler. The primary audience is junior developers and programming students. The application is not a product — it is a living architecture showcase.

Every significant backend operation (DB queries, cache hits, queue messages, worker processing) is surfaced in real time on the frontend so observers can follow what happens under the hood as they play.

> **Core Premise:** A player navigates a dungeon, fights enemies, and levels up — while a transparent backend panel shows each system reacting in real time. The game is the demo. The demo is the game.

### Goals
- Demonstrate a production-grade async Python backend to beginner programmers
- Show RabbitMQ message flow, Redis caching, and SQLAlchemy queries as visible, traceable events
- Produce a codebase that is clean enough to read and learn from
- Generate a frontend that an AI can scaffold entirely from the API contract

### Non-Goals
- Real-time multiplayer
- Mobile support
- User accounts beyond a basic session
- Pixel art, sound, or rich media — text and UI components only

---

## 2. Technology Stack

| Layer      | Technology                  | Role                                          |
|------------|-----------------------------|-----------------------------------------------|
| API        | FastAPI + Uvicorn            | Async HTTP, WebSocket for live backend feed   |
| ORM        | SQLAlchemy 2.0 (async)       | All DB reads/writes, session management       |
| Validation | Pydantic v2                  | Request/response schemas, settings            |
| Database   | PostgreSQL                   | Persistent game state, player data            |
| Cache      | Redis                        | Session tokens, dungeon map cache, leaderboard|
| Queue      | RabbitMQ + aio-pika          | Async jobs: XP events, loot rolls             |
| Workers    | Python consumers             | Consume queue messages, update DB             |
| Admin      | SQLAdmin (FastAPI-native)    | Inspect and edit game data                    |
| Infra      | Docker Compose               | Single-server deployment                      |

> SQLAdmin is used instead of Django Admin to keep the stack unified under FastAPI.

---

## 3. Features

### 3.1 Character & Session
- Player creates a character with a name and class (Warrior, Rogue, Mage)
- Character stats (HP, ATK, DEF, level, XP) persisted in PostgreSQL
- Session token issued and stored in Redis with TTL

### 3.2 Dungeon Navigation
- Procedurally generated dungeon rooms stored in DB at session start
- Player moves between rooms via directional commands (N/S/E/W)
- Room data cached in Redis after first load — cache hit/miss surfaced on frontend

### 3.3 Combat
- Turn-based: player attacks, enemy responds
- Damage calculated server-side with Pydantic-validated schemas
- On enemy death: loot roll and XP award published to RabbitMQ queue
- Worker consumes the event, updates inventory and XP in DB asynchronously

### 3.4 Progression
- XP thresholds trigger level-up events (also via queue)
- Leaderboard of top characters stored and ranked in Redis sorted set
- All progression events appear in the backend activity feed

### 3.5 Backend Transparency Feed

The core educational feature. A live panel on the frontend streams backend events via WebSocket.

| Event Type     | Trigger                        | Message shown to user                              |
|----------------|--------------------------------|----------------------------------------------------|
| DB Write       | Player moves, takes damage     | `Writing player state to PostgreSQL...`            |
| DB Read        | Room loaded for first time     | `Querying dungeon room #14 from DB...`             |
| Cache Hit      | Room already visited           | `Redis cache hit — room loaded in 0.3ms`           |
| Cache Miss     | First visit to room            | `Cache miss — fetching from DB, caching result`    |
| Queue Publish  | Enemy defeated                 | `Publishing loot_roll event to RabbitMQ...`        |
| Queue Consume  | Worker picks up message        | `Worker consumed loot_roll — processing...`        |
| Worker Done    | Loot added to inventory        | `Inventory updated, XP +120 committed to DB`       |

---

## 4. API Contract

All endpoints versioned under `/api/v1`. All bodies are JSON with Pydantic-enforced schemas.

### 4.1 Auth & Session

| Method | Endpoint               | Description                        | Auth  |
|--------|------------------------|------------------------------------|-------|
| POST   | /api/v1/session/start  | Create character, issue token      | None  |
| GET    | /api/v1/session/me     | Get current character state        | Token |
| DELETE | /api/v1/session/end    | End session, clear Redis token     | Token |

### 4.2 Dungeon

| Method | Endpoint               | Description                        | Auth  |
|--------|------------------------|------------------------------------|-------|
| GET    | /api/v1/dungeon/room   | Get current room (cache-aware)     | Token |
| POST   | /api/v1/dungeon/move   | Move: `{ direction: N\|S\|E\|W }`  | Token |
| GET    | /api/v1/dungeon/map    | Get visited room layout            | Token |

### 4.3 Combat

| Method | Endpoint               | Description                        | Auth  |
|--------|------------------------|------------------------------------|-------|
| GET    | /api/v1/combat/state   | Current combat state               | Token |
| POST   | /api/v1/combat/attack  | Player attacks current enemy       | Token |
| POST   | /api/v1/combat/flee    | Attempt to flee combat             | Token |

### 4.4 Character & Inventory

| Method | Endpoint                      | Description                        | Auth  |
|--------|-------------------------------|------------------------------------|-------|
| GET    | /api/v1/character/stats       | HP, ATK, DEF, level, XP            | Token |
| GET    | /api/v1/character/inventory   | List of held items                 | Token |
| GET    | /api/v1/character/leaderboard | Top 10 from Redis sorted set       | None  |

### 4.5 WebSocket — Backend Feed

```
WS /api/v1/feed
```

Persistent read-only stream. Server pushes `BackendEvent` objects on every significant backend operation. No client messages expected.

**BackendEvent schema:**
```json
{
  "event": "cache_hit | cache_miss | db_read | db_write | queue_publish | queue_consume | worker_done",
  "message": "string",
  "duration_ms": "number | null",
  "timestamp": "ISO8601"
}
```

---

## 5. Data Models

### 5.1 SQLAlchemy Models

| Model         | Key Fields                                              | Notes                    |
|---------------|---------------------------------------------------------|--------------------------|
| Player        | id, name, class, hp, max_hp, atk, def, level, xp       | Central entity           |
| DungeonRoom   | id, session_id, x, y, description, enemy_id, is_cleared| Generated per session    |
| Enemy         | id, name, hp, atk, def, xp_reward, loot_table_id       | Seeded, not per-session  |
| InventoryItem | id, player_id, item_id, quantity                        | Junction table           |
| Item          | id, name, type, stat_bonus, description                 | Seeded item definitions  |

### 5.2 Redis Keys

| Key Pattern                    | Type        | TTL  | Contains                          |
|--------------------------------|-------------|------|-----------------------------------|
| `session:{token}`              | Hash        | 24h  | player_id, created_at             |
| `room:{session_id}:{x}:{y}`   | Hash        | 1h   | Cached room data                  |
| `leaderboard`                  | Sorted Set  | None | player_id scored by level+xp      |

### 5.3 RabbitMQ Message Schemas

| Queue       | Published by             | Consumed by          | Payload                              |
|-------------|--------------------------|----------------------|--------------------------------------|
| loot_roll   | Combat route on kill     | loot_worker          | `{ player_id, loot_table_id, xp }`   |
| xp_event    | loot_worker after XP     | level_worker         | `{ player_id, new_xp, current_level }`|
| feed_event  | Any service              | WS broadcaster       | BackendEvent object                  |

---

## 6. Frontend Notes for AI Generation

### 6.1 Layout
- Two-column layout: left = game interface, right = backend activity feed
- Game column: room description, enemy status, player stats, action buttons
- Feed column: scrolling log of BackendEvent messages, colour-coded by event type
- Tailwind utility classes are sufficient — no custom CSS framework needed

### 6.2 Feed Colour Coding

| Event Type                    | Colour | Meaning                  |
|-------------------------------|--------|--------------------------|
| db_read / db_write            | Blue   | Database operation       |
| cache_hit                     | Green  | Fast path taken          |
| cache_miss                    | Amber  | Fallback to DB           |
| queue_publish                 | Purple | Message sent to broker   |
| queue_consume / worker_done   | Pink   | Async worker activity    |

### 6.3 State Management
- Session token stored in memory (not localStorage)
- Player stats polled on each action response — no separate polling loop needed
- WebSocket opened on session start, closed on session end
- Combat state derived from `GET /combat/state` — poll after each action

### 6.4 Page-to-Endpoint Mapping

Each UI section maps to exactly one or two endpoints:

| UI Section     | Endpoints used                              |
|----------------|---------------------------------------------|
| SessionPage    | POST /session/start                         |
| DungeonPage    | GET /dungeon/room, POST /dungeon/move        |
| CombatPanel    | GET /combat/state, POST /combat/attack       |
| StatsPanel     | GET /character/stats, GET /character/inventory|
| FeedPanel      | WS /feed                                    |
| Leaderboard    | GET /character/leaderboard                  |

---

## 7. Deployment

Single-server via Docker Compose. No cloud provider required for demo purposes.

### 7.1 Services

| Service    | Image                     | Port          | Depends On           |
|------------|---------------------------|---------------|----------------------|
| api        | custom build              | 8000          | db, redis, rabbitmq  |
| worker     | same image, different cmd | —             | db, redis, rabbitmq  |
| db         | postgres:16               | 5432          | —                    |
| redis      | redis:7-alpine            | 6379          | —                    |
| rabbitmq   | rabbitmq:3-management     | 5672 / 15672  | —                    |
| nginx      | nginx:alpine              | 80            | api                  |

### 7.2 Environment Variables

```
DATABASE_URL   — async postgres connection string
REDIS_URL      — redis://redis:6379
RABBITMQ_URL   — amqp://guest:guest@rabbitmq/
SECRET_KEY     — JWT signing secret
DEBUG          — enables SQL echo and verbose logging
```

---

## 8. Milestones

| Phase | Deliverable        | Includes                                                    |
|-------|--------------------|-------------------------------------------------------------|
| 1     | Infrastructure     | Docker Compose up, DB migrations, Redis + RabbitMQ connected|
| 2     | Core Game Loop     | Session, dungeon generation, movement, room caching         |
| 3     | Combat + Queue     | Combat endpoints, enemy death events, loot worker           |
| 4     | Feed + WebSocket   | BackendEvent system, WS broadcaster, feed_event queue       |
| 5     | Frontend           | AI-generated UI from this PRD, all panels wired to API      |
| 6     | Polish             | SQLAdmin panel, leaderboard, error handling, demo script    |
