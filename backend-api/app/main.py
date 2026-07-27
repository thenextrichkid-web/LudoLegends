from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os

from app.core.database import engine, Base
from app.api import auth_router, tournaments_router, wallet_router, matches_router, referrals_router, users_router, admin_router, auto_move_router
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Ludo Legends API",
    description="Backend API for Ludo Legends Tournament Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tournaments_router)
app.include_router(wallet_router)
app.include_router(matches_router)
app.include_router(referrals_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(auto_move_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


WEB_DIR = Path("/app/web")
ADMIN_DIR = Path("/app/admin")
if ADMIN_DIR.exists():
    app.mount("/admin", StaticFiles(directory=str(ADMIN_DIR), html=True), name="admin")
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
