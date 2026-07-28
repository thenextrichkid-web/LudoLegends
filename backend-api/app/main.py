"""Ludo Legends API — FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.database import engine, Base
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.metrics import metrics
from app.core.crash_reporter import CrashContext
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import register_error_handlers
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.api import (
    auth_router, tournaments_router, wallet_router, matches_router,
    referrals_router, users_router, admin_router, auto_move_router,
    withdrawals_router, admin_config_router, feature_flags_router,
    admin_audit_router, notifications_router, metrics_router,
    queue_router,
)
from app.api.health import router as health_router, set_version

settings = get_settings()
setup_logging(settings.ENVIRONMENT)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.core.database import async_session
    async with async_session() as db:
        from app.services.feature_flag_service import FeatureFlagService
        from app.services.config_service import ConfigService
        await FeatureFlagService(db).seed_defaults()
        await ConfigService(db).seed_defaults()
        await db.commit()

    import asyncio
    queue_expiry_task = None

    async def _expire_loop():
        while True:
            try:
                from app.core.database import async_session
                async with async_session() as db:
                    from app.services.queue_service import QueueService
                    count = await QueueService(db).expire_stale_entries()
                    if count > 0:
                        await db.commit()
                        logger.info("Queue expiry: %d entries expired", count)
            except Exception as e:
                logger.error("Queue expiry task error: %s", e)
            await asyncio.sleep(30)

    queue_expiry_task = asyncio.create_task(_expire_loop())
    logger.info("Queue expiry background task started")

    logger.info("Ludo Legends API started — version=%s env=%s", settings.VERSION, settings.ENVIRONMENT)
    yield
    if queue_expiry_task:
        queue_expiry_task.cancel()
    logger.info("Ludo Legends API shutting down")


set_version(settings.VERSION)

app = FastAPI(
    title="Ludo Legends API",
    description=(
        "Backend API for Ludo Legends Tournament Platform.\n\n"
        "## Authentication\n"
        "All protected endpoints require a Bearer token in the Authorization header.\n\n"
        "## Error Format\n"
        "All errors return:\n"
        "```json\n{\"success\": false, \"code\": \"ERROR_CODE\", \"message\": \"...\", \"requestId\": \"...\"}\n```\n\n"
        "## Feature Flags\n"
        "Use `GET /api/admin/feature-flags/public` to check enabled features."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)

register_error_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(tournaments_router)
app.include_router(wallet_router)
app.include_router(matches_router)
app.include_router(referrals_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(auto_move_router)
app.include_router(withdrawals_router)
app.include_router(admin_config_router)
app.include_router(feature_flags_router)
app.include_router(admin_audit_router)
app.include_router(notifications_router)
app.include_router(metrics_router)
app.include_router(queue_router)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    import time
    start = time.time()
    metrics.increment("http_requests_total")
    path = request.url.path
    if "/api/" in path:
        metrics.increment(f"api_requests:{path.split('/')[2] if len(path.split('/')) > 2 else 'other'}")

    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    metrics.observe("http_latency_ms", elapsed)

    status = response.status_code
    metrics.increment(f"http_status:{status}")
    if status >= 500:
        metrics.increment("http_errors_5xx")
    elif status >= 400:
        metrics.increment("http_errors_4xx")

    return response


APK_PATH = Path("/app/apk/LudoLegends.apk")


@app.get("/download/apk", tags=["system"])
async def download_apk():
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
