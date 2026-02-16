# POTA Hunter Logger

A Parks on the Air (POTA) **hunter** logging application for logging contacts with park activators from home. Built with a FastAPI backend, PostgreSQL database, and React frontend.

## Features

- **Active Spots Browser** — real-time feed of active POTA activators with band/mode filtering; click a spot to auto-fill the QSO form
- **QSO Logging** — log contacts with park reference, callsign, frequency (auto-detects band), mode, and RST
- **Park Lookup** — debounced lookup against the POTA API shows park names as you type
- **Duplicate Prevention** — unique constraint on callsign + park + band per session (409 on duplicates)
- **ADIF Export** — download contacts in ADIF v3.1.4 hunter format (`SIG=POTA`, `SIG_INFO` per QSO)
- **Daily Sessions** — one hunt session per day, auto-created on first visit

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (via nvm: `nvm use 20`)

## Quick Start

```bash
# Start backend + database
docker compose up -d

# Start frontend
cd frontend && npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

On first visit, you'll be prompted to enter your operator callsign.

## Development

```bash
# Rebuild backend after code changes
docker compose up -d --build

# Stop everything
docker compose down

# Reset database (drops all data)
docker compose down
docker volume rm claude-pota-logger_pgdata
docker compose up -d --build
```

## Architecture

| Layer | Technology | Runs in |
|-------|-----------|---------|
| Backend | FastAPI (Python 3.12), async SQLAlchemy + asyncpg | Docker |
| Database | PostgreSQL 16 | Docker |
| Frontend | React + TypeScript + Vite | Local (npm) |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/hunt-sessions/today` | Auto-create or return today's session |
| GET | `/api/hunt-sessions` | List all sessions |
| GET | `/api/hunt-sessions/{id}` | Get session with QSOs |
| POST | `/api/hunt-sessions/{id}/qsos` | Log a QSO |
| GET | `/api/hunt-sessions/{id}/qsos` | List QSOs |
| DELETE | `/api/hunt-sessions/{id}/qsos/{qso_id}` | Delete a QSO |
| GET | `/api/hunt-sessions/{id}/export` | Download ADIF file |
| GET | `/api/settings` | Get operator settings |
| PUT | `/api/settings` | Update operator callsign |
| GET | `/api/parks/{park_ref}` | Park name/location lookup |
| GET | `/api/spots` | Active POTA activator spots |
