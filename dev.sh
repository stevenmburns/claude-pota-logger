#!/bin/bash
trap 'kill 0' EXIT

cd backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
cd frontend && npm run dev &
wait
