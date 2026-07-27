#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "
import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect('postgresql://postgres:postgres@db:5432/ludo_legends')
    await conn.close()
asyncio.run(check())
" 2>/dev/null; do
  sleep 2
done
echo "Database is ready."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running seed data..."
python -m seed

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
