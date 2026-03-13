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