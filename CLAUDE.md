# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

POTA Hunter Logger — a Parks on the Air (POTA) **hunter** logging application with a FastAPI backend, SQLite database, and React frontend. Designed for logging contacts with park activators from home (not for activating parks).

## Architecture

- **Backend**: FastAPI (Python 3.12) with async SQLAlchemy + aiosqlite, runs directly via uvicorn
- **Database**: SQLite (file: `backend/pota.db`), created automatically on first backend startup
- **Frontend**: React + TypeScript + Vite, runs locally via `npm run dev`

## Project Structure

```
backend/
  app/
    main.py           # FastAPI app entry point, CORS config, lifespan (auto-creates tables)
    models.py          # SQLAlchemy ORM models (HuntSession, QSO, Settings); SQLiteUUID TypeDecorator
    schemas.py         # Pydantic v2 request/response schemas
    database.py        # Async engine + session factory (defaults to sqlite+aiosqlite:///pota.db)
    adif.py            # ADIF v3.1.4 file generation (hunter format: SIG/SIG_INFO per QSO)
    routers/
      hunt_sessions.py # Hunt session endpoints (auto-create today's, list, get)
      qsos.py          # QSO CRUD endpoints (409 on duplicate call/park/band)
      export.py        # ADIF export endpoint
      settings.py      # Operator callsign + flrig host/port settings (singleton)
      parks.py         # Proxy to POTA park API for park name lookup
      spots.py         # Proxy to POTA activator spots API (real-time, server-side band/mode filtering, hunted flag from today's QSOs)
      radio.py         # POST /api/radio/set-frequency — proxies XML-RPC call to flrig rig control
  tests/
    conftest.py        # Async SQLite test fixtures, FastAPI test client
    test_adif.py       # Unit tests for ADIF generation
    test_band_conversion.py  # Unit tests for kHz-to-band conversion
    test_hunt_sessions.py    # Integration tests for session endpoints
    test_qsos.py             # Integration tests for QSO CRUD + duplicate prevention
    test_settings.py         # Integration tests for settings endpoints
    test_export.py           # Integration tests for ADIF export
    test_parks.py            # Mocked POTA API park proxy tests
    test_spots.py            # Mocked POTA API spots + hunted flag tests
    test_radio.py            # Mocked flrig XML-RPC tests for set-frequency endpoint
  requirements.txt
  requirements-test.txt  # Test dependencies (pytest, pytest-asyncio, respx); inherits requirements.txt
  pytest.ini             # pytest configuration

.github/
  workflows/
    backend-tests.yml  # CI: runs pytest on push to main and PRs (Python 3.12, in-memory SQLite)

frontend/
  src/
    App.tsx            # Root component with global styles
    api.ts             # Fetch wrapper for backend calls
    types.ts           # TypeScript types matching backend schemas
    pages/Home.tsx     # Main page (auto-loads today's session, settings check)
    components/
      SettingsForm.tsx  # Operator callsign + flrig host/port setup; shown on first use or via Settings button; accepts currentSettings prop for pre-population
      QSOForm.tsx       # Log a QSO; fields: Band, Freq, Mode, Callsign, RST Sent, RST Rcvd, Park Ref (with POTA API lookup, auto band-from-freq)
      QSOTable.tsx      # List/delete QSOs; columns: #, UTC, Band, Freq, Mode, Callsign, RST S, RST R, Park
      ExportButton.tsx  # ADIF download
      SpotsList.tsx     # Browse active POTA spots; columns: Hunted, UTC, Freq, Mode, Activator, Location, Park, Name; sorted by freq/activator/time; band/mode filter dropdowns trigger backend re-fetch; click row to fill QSO form and focus RST Sent; click Freq cell to also set radio via flrig; hunted spots shown with checkmark and green background; refreshes on QSO create/delete
  vite.config.ts      # Proxies /api to localhost:8000
```

## Data Model

- **HuntSession**: One per day (unique `session_date`), auto-created on first visit
- **QSO**: Linked to a hunt session; includes `park_reference` per contact. Unique constraint on `(hunt_session_id, callsign, park_reference, band)` prevents duplicate logs
- **Settings**: Singleton storing `operator_callsign`, `flrig_host` (default `localhost`), and `flrig_port` (default `12345`) — global, not per-session

## Environment Prerequisites

- **Node 20+** is required for the frontend (Vite 6). Use `nvm use 20` before running `npm` commands.
- **Python 3.12** with dependencies in `backend/.venv` is required for the backend.
- **gh CLI** is required for PR workflows (`gh pr create`, `gh pr merge`).
- Before starting work, verify the environment: `node --version` (must be 20+), `gh --version` (installed and authenticated).

## Development Commands

```bash
# Start backend (runs directly, auto-reloads on code changes; creates backend/pota.db on first run)
cd backend
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (requires Node 20+ via nvm)
cd frontend && npm run dev
# Frontend runs at http://localhost:5173, backend at http://localhost:8000

# Reset database (drops all data, recreates on next backend startup)
rm backend/pota.db
```

## Testing

```bash
# Install test dependencies (one-time setup)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-test.txt

# Run all tests (~2s, no database needed)
cd backend && source .venv/bin/activate && pytest -v
```

Tests use in-memory SQLite (via aiosqlite). External POTA API calls are mocked with respx. No running database is required.

CI runs automatically via GitHub Actions on pushes to `main` and PRs when `backend/` or the workflow file changes.

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
| PUT | `/api/settings` | Update operator callsign, flrig host/port |
| GET | `/api/parks/{park_ref}` | Proxy to POTA park API (returns park name/location) |
| GET | `/api/spots` | Proxy to POTA activator spots API; optional `band` and `mode` query params for server-side filtering; each spot includes `hunted` flag based on today's QSOs |
| POST | `/api/radio/set-frequency` | Set radio frequency via flrig XML-RPC; body: `{ frequency_khz: number }`; returns 503 if flrig unreachable |

## Git Workflow

- Always create feature branches for changes — never push directly to main unless explicitly asked.
- Use the `/pr` skill to automate the full PR lifecycle (branch, commit, push, create PR, merge, cleanup).
- Commit messages should be descriptive and conventional (e.g., "Add hunted indicator to spots list").

## Documentation

- Always update README.md and CLAUDE.md when adding or changing features, API endpoints, or UI components.
- Keep the Project Structure section in CLAUDE.md in sync with actual file descriptions.

## Key Details

- CORS allows `http://localhost:5173` (Vite dev server)
- Tables are auto-created on backend startup (no migrations yet)
- Node 20 is required; use `nvm use 20` (nvm is installed)
- Database: SQLite file at `backend/pota.db`; created automatically on first backend startup
- First visit prompts for operator callsign; stored globally in Settings table
- Park reference input does a debounced lookup against the POTA API to show park names
- ADIF export uses hunter format: `SIG=POTA`, `SIG_INFO=<hunted park>`, `STATION_CALLSIGN=<operator>`
- Active spots panel fetches from POTA API on load and auto-refreshes every 60 seconds; band/mode filtering is done server-side (backend converts kHz to band); click a spot row to auto-fill the QSO form and focus RST Sent input; click the Freq cell specifically to also tune the radio via flrig
- Spots are annotated with a `hunted` flag (backend matches activator/park/band against today's QSOs); hunted spots display a checkmark and green background; spots list refreshes immediately after logging or deleting a QSO
- flrig integration: backend proxies XML-RPC to flrig (default `localhost:12345`); since the backend runs directly on the host, it can reach flrig/mock on localhost without any special networking; frequency in kHz is converted to Hz before calling `rig.set_vfo`; 503 returned if flrig unreachable
