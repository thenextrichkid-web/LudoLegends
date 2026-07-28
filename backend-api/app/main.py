"""Ludo Legends API — FastAPI application entry point."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.database import engine, Base
from app.core.config import get_settings
from app.api import (
    auth_router, tournaments_router, wallet_router, matches_router,
    referrals_router, users_router, admin_router, auto_move_router,
    withdrawals_router,
)
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Ludo Legends API",
    description="Backend API for Ludo Legends Tournament Platform",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
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
app.include_router(withdrawals_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


APK_PATH = Path("/app/apk/LudoLegends.apk")


@app.get("/download/apk")
async def download_apk():
    """Download the latest APK build."""
    if APK_PATH.exists():
        return FileResponse(
            path=str(APK_PATH),
            media_type="application/vnd.android.package-archive",
            filename="LudoLegends.apk",
        )
    raise HTTPException(status_code=404, detail="APK not found")


WEB_DIR = Path("/app/web")
ADMIN_DIR = Path("/app/admin")
if ADMIN_DIR.exists():
    app.mount("/admin", StaticFiles(directory=str(ADMIN_DIR), html=True), name="admin")
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
