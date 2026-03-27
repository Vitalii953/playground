# Dungeon Crawler Frontend

Simple vanilla JS frontend for the dungeon crawler game.

## Features

- **Landing Page** (`index.html`)
  - Language selection
  - Creates player via API
  - Starts game session

- **Game Page** (`game.html`)
  - Turn-based gameplay
  - Real-time backend activity feed
  - Item equip/reject decisions
  - Player stats display
  - Terminal aesthetic with CRT effects

## Running

### With Docker Compose (Recommended)
```bash
docker-compose up frontend
```
Access at: http://localhost:3000

### Standalone (for development)
```bash
# Serve with any static server
python -m http.server 3000 --directory frontend

# Or with Node.js
npx serve frontend -p 3000
```

## API Configuration

The frontend automatically detects the environment:
- **localhost**: Uses `http://localhost:8000` (direct backend)
- **Docker**: Uses `http://backend:8000` (container network)

## Architecture

- **No build step** - Pure HTML/CSS/JS
- **Session storage** - Stores session token, player ID, language
- **Responsive** - Works on mobile and desktop
- **Terminal theme** - Green phosphor text, CRT scanlines

## Pages Flow

1. User visits `index.html`
2. Selects language → POST `/create-player` → POST `/start`
3. Redirects to `game.html` with session token
4. Game loop: POST `/turn` → display event → POST `/resolve` (if needed)
5. On death: POST `/end` → redirect to `index.html`

## Backend Events Display

Color-coded by type:
- **Blue** - Database operations (db_read, db_write)
- **Green** - Cache hits (cache_hit, cache_write)
- **Amber** - Cache misses
- **Purple** - Game events (event_trigger)
- **Cyan** - Session events (session_create, session_end)
- **Red** - Player death

## Browser Support

Works in all modern browsers (Chrome, Firefox, Safari, Edge).
Requires ES6+ support for async/await.
