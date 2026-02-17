# POTA Hunter Logger — API & Database Reference

## Backend API (curl commands)

The backend runs at `http://localhost:8000`. All endpoints are prefixed with `/api`.

### Hunt Sessions

**Get or create today's session:**

```bash
curl http://localhost:8000/api/hunt-sessions/today
```

**List all sessions:**

```bash
curl http://localhost:8000/api/hunt-sessions
```

**Get a specific session (with its QSOs):**

```bash
# Replace SESSION_ID with a UUID from the list above
curl http://localhost:8000/api/hunt-sessions/SESSION_ID
```

### QSOs

All QSO endpoints require a session ID. Get one from the hunt sessions endpoints above.

**Log a new QSO:**

```bash
curl -X POST http://localhost:8000/api/hunt-sessions/SESSION_ID/qsos \
  -H "Content-Type: application/json" \
  -d '{
    "callsign": "W1AW",
    "park_reference": "US-0001",
    "frequency": 14.250,
    "band": "20m",
    "mode": "SSB",
    "rst_sent": "59",
    "rst_received": "59",
    "timestamp": "2026-02-17T15:30:00Z"
  }'
```

Returns `201` on success, `409` if you already logged this callsign/park/band combination.

**List QSOs for a session:**

```bash
curl http://localhost:8000/api/hunt-sessions/SESSION_ID/qsos
```

**Delete a QSO:**

```bash
curl -X DELETE http://localhost:8000/api/hunt-sessions/SESSION_ID/qsos/QSO_ID
```

Returns `204` on success.

### Settings

**Get operator settings:**

```bash
curl http://localhost:8000/api/settings
```

**Update operator callsign:**

```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"operator_callsign": "N0CALL"}'
```

### ADIF Export

**Download ADIF file for a session:**

```bash
curl http://localhost:8000/api/hunt-sessions/SESSION_ID/export
```

Save to a file:

```bash
curl -o session.adi http://localhost:8000/api/hunt-sessions/SESSION_ID/export
```

### Park Lookup

**Look up a POTA park by reference:**

```bash
curl http://localhost:8000/api/parks/US-0001
```

### Active Spots

**Get all active POTA spots:**

```bash
curl http://localhost:8000/api/spots
```

**Filter spots by band:**

```bash
curl "http://localhost:8000/api/spots?band=20m"
```

**Filter spots by mode:**

```bash
curl "http://localhost:8000/api/spots?mode=CW"
```

**Filter by both band and mode:**

```bash
curl "http://localhost:8000/api/spots?band=40m&mode=SSB"
```

Each spot in the response includes a `hunted` boolean flag indicating whether you've already logged that activator/park/band combination today.

---

## Direct Database Access (psql)

The PostgreSQL database runs in Docker with these credentials:

| Setting  | Value       |
|----------|-------------|
| Host     | localhost   |
| Port     | 5432        |
| Database | pota        |
| User     | pota        |
| Password | pota        |

### Connect to the database

```bash
psql -h localhost -U pota -d pota
# Enter password: pota
```

Or as a single command (password inline):

```bash
PGPASSWORD=pota psql -h localhost -U pota -d pota
```

Or connect via the running Docker container:

```bash
docker compose exec db psql -U pota -d pota
```

### Useful SQL queries

**List all tables:**

```sql
\dt
```

**Describe a table's columns:**

```sql
\d hunt_sessions
\d qsos
\d settings
```

**Show all hunt sessions:**

```sql
SELECT id, session_date, created_at FROM hunt_sessions ORDER BY session_date DESC;
```

**Show today's session:**

```sql
SELECT * FROM hunt_sessions WHERE session_date = CURRENT_DATE;
```

**Show all QSOs for today's session:**

```sql
SELECT q.timestamp AT TIME ZONE 'UTC' AS utc_time,
       q.callsign, q.park_reference, q.band, q.frequency, q.mode,
       q.rst_sent, q.rst_received
  FROM qsos q
  JOIN hunt_sessions hs ON q.hunt_session_id = hs.id
 WHERE hs.session_date = CURRENT_DATE
 ORDER BY q.timestamp;
```

**Count QSOs per session:**

```sql
SELECT hs.session_date, COUNT(q.id) AS qso_count
  FROM hunt_sessions hs
  LEFT JOIN qsos q ON q.hunt_session_id = hs.id
 GROUP BY hs.session_date
 ORDER BY hs.session_date DESC;
```

**Show unique parks worked:**

```sql
SELECT DISTINCT park_reference, callsign, band
  FROM qsos
 ORDER BY park_reference;
```

**Show operator callsign setting:**

```sql
SELECT operator_callsign, updated_at FROM settings;
```

**Find duplicate-prevention constraint (the unique index):**

```sql
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'qsos';
```
