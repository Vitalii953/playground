# new features: translator api plus caching server-side, durable redis storage

app/
├── core/                  # shared game logic — knows nothing about HTTP
│   ├── combat.py
│   ├── dungeon.py
│   ├── progression.py
│   └── translation.py
│
├── api/                   # FastAPI — thin layer, calls core
│   └── routes/
│       ├── dungeon.py     # calls core.dungeon
│       └── combat.py     # calls core.combat
│
└── workers/               # also calls core, not the API
    └── handlers/
        └── loot.py        # calls core.progression