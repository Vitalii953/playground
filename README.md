# new features: translator api plus caching server-side, durable redis storage
# new rule: NEVER LOG IN HIGH-LEVEL FUNCTIONS!!!!


app/
├── core/                  # shared game logic - knows nothing about HTTP
│   ├── combat.py
│   ├── dungeon.py
│   ├── progression.py
│   └── translation.py
│
├── api/                   # FastAPI - thin layer, calls core
│   └── routes/
│       ├── dungeon.py     # calls core.dungeon
│       └── combat.py     # calls core.combat
│
└── workers/               # also calls core, not the API
    └── handlers/
        └── loot.py        # calls core.progression


# current progress: game WIP. translator finished, all tests pass.
# also, game MANAGES DATA SOLO. API has nothing to do with it. SoC must be respected!
# i decided to abstract away slots and other metadata - they shouldn't figure in phrases.py
# TRANSLATION LAYER: at launch for every user, depending on language, the phrases are either being all translated or not.
#
# Translation caching behavior:
# - `backend/services/translator/translation_service.py.translate` does not write to Redis; it only resolves text.
# - `backend/services/cache_warm.py.warm_cache` generates precomputed strings for non-dynamic phrase values and stores cache
#   entries as `translation:{lang}:{hash(text)}`.
# - Dynamic phrases (containing `{}` markers) are excluded from warm cache via `get_cacheable`.

## Translator API + Redis caching

`/translate` endpoint in `backend/api/main.py`:
 - Query params: `text`, `to_language` (default `en`)
 - Uses `backend.services.translator.translation_service.translate`
 - Reads and writes cache in Redis using `translation:{lang}:{hash(text)}`
 - TTL controlled by `backend/services/translator/config.py` (`cache_time`)

New test: `tests/services/test_translator_api.py`