# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

POTA Logger — a Parks on the Air (POTA) logging application with a FastAPI backend, PostgreSQL database, and React frontend.

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
    models.py          # SQLAlchemy ORM models (Activation, QSO)
    schemas.py         # Pydantic v2 request/response schemas
    database.py        # Async engine + session factory
    adif.py            # ADIF v3.1.4 file generation
    routers/
      activations.py   # Activation CRUD endpoints
      qsos.py          # QSO CRUD endpoints
      export.py        # ADIF export endpoint
  Dockerfile
  requirements.txt

frontend/
  src/
    App.tsx            # Root component with global styles
    api.ts             # Fetch wrapper for backend calls
    types.ts           # TypeScript types matching backend schemas
    pages/Home.tsx     # Main page (activation selector + QSO logging view)
    components/
      ActivationForm.tsx  # Start/select activations
      QSOForm.tsx         # Log a QSO (auto band-from-freq, mode-based RST defaults)
      QSOTable.tsx        # List/delete QSOs
      ExportButton.tsx    # ADIF download
  vite.config.ts      # Proxies /api to localhost:8000
```

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
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/activations` | Create activation |
| GET | `/api/activations` | List activations |
| GET | `/api/activations/{id}` | Get activation with QSOs |
| POST | `/api/activations/{id}/qsos` | Log a QSO |
| GET | `/api/activations/{id}/qsos` | List QSOs |
| DELETE | `/api/activations/{id}/qsos/{qso_id}` | Delete a QSO |
| GET | `/api/activations/{id}/export` | Download ADIF file |

## Key Details

- CORS allows `http://localhost:5173` (Vite dev server)
- Tables are auto-created on backend startup (no migrations yet)
- Node 20 is required; use `nvm use 20` (nvm is installed)
- Database credentials: `pota/pota` on `localhost:5432`, database `pota`
