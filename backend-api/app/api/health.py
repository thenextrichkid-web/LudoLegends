"""Health check endpoints — /health, /ready, /live with dependency checks."""

import time
import os
from datetime import datetime, timezone
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(tags=["system"])

_startup_time = time.time()
_VERSION = "1.0.0"


def set_version(v: str):
    global _VERSION
    _VERSION = v


async def _check_database() -> dict:
    from app.core.database import async_session
    start = time.time()
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "up", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        return {"status": "down", "error": str(e)}


async def _check_redis() -> dict:
    from app.core.config import get_settings
    settings = get_settings()
    start = time.time()
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=3)
        await r.ping()
        await r.aclose()
        return {"status": "up", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        return {"status": "down", "error": str(e)}


def _check_disk() -> dict:
    try:
        stat = os.statvfs("/")
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used_pct = round(((total - free) / total) * 100, 1) if total > 0 else 0
        return {
            "status": "up" if used_pct < 90 else "warning",
            "used_percent": used_pct,
            "free_gb": round(free / (1024 ** 3), 2),
        }
    except Exception as e:
        return {"status": "down", "error": str(e)}


def _check_memory() -> dict:
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        mem = {}
        for line in lines:
            parts = line.split()
            if parts[0] in ("MemTotal:", "MemAvailable:", "MemFree:"):
                mem[parts[0]] = int(parts[1]) * 1024
        total = mem.get("MemTotal:", 0)
        available = mem.get("MemAvailable:", 0)
        used_pct = round(((total - available) / total) * 100, 1) if total > 0 else 0
        return {
            "status": "up" if used_pct < 90 else "warning",
            "used_percent": used_pct,
            "available_gb": round(available / (1024 ** 3), 2),
        }
    except FileNotFoundError:
        import psutil
        vm = psutil.virtual_memory()
        return {
            "status": "up" if vm.percent < 90 else "warning",
            "used_percent": vm.percent,
            "available_gb": round(vm.available / (1024 ** 3), 2),
        }
    except Exception as e:
        return {"status": "down", "error": str(e)}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": _VERSION, "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/ready")
async def readiness_check():
    db_check = await _check_database()
    redis_check = await _check_redis()
    disk_check = _check_disk()
    memory_check = _check_memory()

    all_ok = all(c["status"] in ("up", "warning") for c in [db_check, redis_check, disk_check, memory_check])

    return {
        "status": "ready" if all_ok else "not_ready",
        "version": _VERSION,
        "uptime_seconds": round(time.time() - _startup_time, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "database": db_check,
            "redis": redis_check,
            "disk": disk_check,
            "memory": memory_check,
        },
    }


@router.get("/live")
async def liveness_check():
    return {
        "status": "alive",
        "version": _VERSION,
        "uptime_seconds": round(time.time() - _startup_time, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
