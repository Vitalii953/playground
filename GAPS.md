# Current Gaps in Playground App

## Critical Issues (Must Fix for MVP)

### 1. **Database Persistence is Missing**
- **Problem**: POST `/items` endpoint queues messages to RabbitMQ but **never saves to the database**
- **Current Flow**: `POST /items` → RabbitMQ → Redis (no DB)
- **Should Be**: `POST /items` → DB (save immediately) + RabbitMQ (async work)
- **Impact**: All data is ephemeral; restarting loses everything
- **Location**: `app/main.py` line ~40 (POST endpoint)

### 2. **CRUD Functions Are Defined But Never Used**
- **Problem**: `app/crud.py` exists with `create_item()`, `get_item()`, `get_items()` but none are imported or called
- **Should Be**: All API endpoints use CRUD functions
- **Impact**: No way to read data from database; API is incomplete
- **Location**: `app/crud.py` (unused file)

### 3. **No GET Endpoints for Reading Data**
- **Problem**: Only POST `/items` exists
- **Should Be**: 
  - `GET /items` (list all items)
  - `GET /items/{item_id}` (get single item)
- **Impact**: Data is write-only; can't retrieve what was saved
- **Location**: `app/main.py` (missing routes)

### 4. **Worker Doesn't Validate Messages**
- **Problem**: `app/worker.py` stores raw JSON strings in Redis without schema validation
- **Should Be**: Parse message, validate against `ItemResponse` schema, store structured data
- **Current**: `await redis_client.lpush(settings.redis_items_key, message.body.decode())`
- **Impact**: Invalid/corrupt messages accepted; no type safety
- **Location**: `app/worker.py` line ~30-35

### 5. **No Error Handling or Validation**
- **Problem**: No try-catch blocks, no input validation, no HTTP exception handlers
- **Should Be**: 
  - Validate request payloads
  - Return proper HTTP error codes
  - Log exceptions
- **Impact**: Crashes aren't graceful; unclear what went wrong
- **Location**: `app/main.py`, `app/worker.py`

## High Priority Issues

### 6. **No Logging Strategy**
- **Problem**: No logs anywhere; hard to debug in production
- **Should Be**: `logging` module configured with levels
- **Location**: All modules

### 7. **Tests Are Mocking the Message Broker**
- **Problem**: `tests/test_api_enqueue.py` uses a mock for RabbitMQ; no real integration tests
- **Should Be**: Tests that verify end-to-end flow with real RabbitMQ
- **Impact**: Doesn't test real async behavior
- **Location**: `tests/`

### 8. **Django Admin Container Not Configured**
- **Problem**: `docker-compose.yml` defines Django service but it's not set up
- **Should Be**: Either remove it or configure admin panel for item management
- **Impact**: Dead code in docker-compose
- **Location**: `docker-compose.yml` (Django service)

## Medium Priority Issues

### 9. **No Database Index Strategy**
- **Problem**: Models defined but no indexes on frequently queried columns
- **Should Be**: Index on `id`, maybe `created_at`
- **Location**: `app/models.py`

### 10. **No Pagination or Filtering**
- **Problem**: `GET /items` would return all items with no limits
- **Should Be**: Support `offset`, `limit`, optional filtering
- **Location**: `app/main.py` (future routes)

### 11. **Database Connection Pool Not Configured**
- **Problem**: `engine = create_async_engine(str(settings.database_url))` uses defaults
- **Should Be**: Configure `pool_size`, `max_overflow`, timeouts
- **Location**: `app/database.py` line ~12

## Low Priority (Nice to Have)

### 12. **No API Documentation Beyond Auto-Docs**
- **Problem**: Only FastAPI's auto-generated `/docs` exists
- **Should Be**: README with examples, deployment guide

### 13. **No Health Check for Dependencies**
- **Problem**: `/health` exists but only checks if app is running
- **Should Be**: Check DB, RabbitMQ, Redis connectivity
- **Location**: `app/main.py` line ~20

### 14. **No Graceful Shutdown**
- **Problem**: Lifespan handles startup but shutdown could be more robust
- **Should Be**: Ensure all connections close, pending messages finish
- **Location**: `app/main.py` (lifespan context)

---

## Implementation Roadmap

### Phase 1: MVP (This Session) 
- [x] Understand current architecture
- [ ] Add DB persistence to POST endpoint
- [ ] Create GET `/items` and `GET /items/{id}` endpoints
- [ ] Use CRUD functions in all routes
- [ ] Add basic error handling

### Phase 2: Quality (Next)
- [ ] Improve worker validation
- [ ] Add logging
- [ ] Write integration tests
- [ ] Configure database pool

### Phase 3: Polish (Later)
- [ ] Admin panel or health checks
- [ ] Pagination/filtering
- [ ] Documentation
- [ ] Performance optimization

---

## Files That Need Changes

| File | Issue | Priority |
|------|-------|----------|
| `app/main.py` | Missing GET endpoints, no DB save, no error handling | **CRITICAL** |
| `app/crud.py` | Functions exist but unused | **CRITICAL** |
| `app/worker.py` | No validation, raw string storage | **HIGH** |
| `app/database.py` | Pool not configured | MEDIUM |
| `tests/test_api_enqueue.py` | Mocks only; no integration tests | HIGH |
| `app/models.py` | No indexes | MEDIUM |
| All files | No logging | HIGH |
