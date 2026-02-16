# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

POTA Hunter Logger — a Parks on the Air (POTA) **hunter** logging application with a FastAPI backend, PostgreSQL database, and React frontend. Designed for logging contacts with park activators from home (not for activating parks).

## Architecture

- **Backend**: FastAPI (Python 3.12) with async SQLAlchemy + asyncpg, runs in Docker
- **Database**: PostgreSQL 16, runs in Docker
- **Frontend**: React + TypeScript + Vite, runs locally via `npm run dev`
- Docker Compose orchestrates backend + database; frontend runs outside Docker

## Project Structure

```
backend/
  app/
    main.py           # FastAPI app entry point, CORS config, lifespan (auto-creates tables)
    models.py          # SQLAlchemy ORM models (HuntSession, QSO, Settings)
    schemas.py         # Pydantic v2 request/response schemas
    database.py        # Async engine + session factory
    adif.py            # ADIF v3.1.4 file generation (hunter format: SIG/SIG_INFO per QSO)
    routers/
      hunt_sessions.py # Hunt session endpoints (auto-create today's, list, get)
      qsos.py          # QSO CRUD endpoints (409 on duplicate call/park/band)
      export.py        # ADIF export endpoint
      settings.py      # Operator callsign settings (singleton)
      parks.py         # Proxy to POTA park API for park name lookup
      spots.py         # Proxy to POTA activator spots API (real-time)
  Dockerfile
  requirements.txt

frontend/
  src/
    App.tsx            # Root component with global styles
    api.ts             # Fetch wrapper for backend calls
    types.ts           # TypeScript types matching backend schemas
    pages/Home.tsx     # Main page (auto-loads today's session, settings check)
    components/
      SettingsForm.tsx  # Operator callsign setup (shown on first use)
      QSOForm.tsx       # Log a QSO (park ref with POTA API lookup, auto band-from-freq)
      QSOTable.tsx      # List/delete QSOs (includes Park column)
      ExportButton.tsx  # ADIF download
      SpotsList.tsx     # Browse active POTA spots with band/mode filtering; click to fill QSO form
  vite.config.ts      # Proxies /api to localhost:8000
```

## Data Model

- **HuntSession**: One per day (unique `session_date`), auto-created on first visit
- **QSO**: Linked to a hunt session; includes `park_reference` per contact. Unique constraint on `(hunt_session_id, callsign, park_reference, band)` prevents duplicate logs
- **Settings**: Singleton storing `operator_callsign` (global, not per-session)

## Development Commands

```bash
# Start backend + database
docker compose up -d

# Start frontend (requires Node 20+ via nvm)
cd frontend && npm run dev
# Frontend runs at http://localhost:5173, backend at http://localhost:8000

# Rebuild backend after code changes
docker compose up -d --build

# Stop everything
docker compose down

# Reset database (drops all data, recreates tables on next startup)
docker compose down
docker volume rm claude-pota-logger_pgdata
docker compose up -d --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/hunt-sessions/today` | Auto-create or return today's session |
| GET | `/api/hunt-sessions` | List all sessions |
| GET | `/api/hunt-sessions/{id}` | Get session with QSOs |
| POST | `/api/hunt-sessions/{id}/qsos` | Log a QSO (409 on duplicate) |
| GET | `/api/hunt-sessions/{id}/qsos` | List QSOs |
| DELETE | `/api/hunt-sessions/{id}/qsos/{qso_id}` | Delete a QSO |
| GET | `/api/hunt-sessions/{id}/export` | Download ADIF file |
| GET | `/api/settings` | Get operator settings (auto-creates default) |
| PUT | `/api/settings` | Update operator callsign |
| GET | `/api/parks/{park_ref}` | Proxy to POTA park API (returns park name/location) |
| GET | `/api/spots` | Proxy to POTA activator spots API (real-time active activators) |

## Key Details

- CORS allows `http://localhost:5173` (Vite dev server)
- Tables are auto-created on backend startup (no migrations yet)
- Node 20 is required; use `nvm use 20` (nvm is installed)
- Database credentials: `pota/pota` on `localhost:5432`, database `pota`
- First visit prompts for operator callsign; stored globally in Settings table
- Park reference input does a debounced lookup against the POTA API to show park names
- ADIF export uses hunter format: `SIG=POTA`, `SIG_INFO=<hunted park>`, `STATION_CALLSIGN=<operator>`
- Active spots panel fetches from POTA API on load and auto-refreshes every 60 seconds; click a spot to auto-fill the QSO form
