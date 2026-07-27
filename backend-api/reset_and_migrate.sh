#!/bin/bash
# Reset DB and generate initial Alembic migration
python -c "
import asyncio
from app.core.database import engine, Base
from app.models import *
async def drop():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
asyncio.run(drop())
"
alembic stamp head
alembic revision --autogenerate -m "initial_schema"
