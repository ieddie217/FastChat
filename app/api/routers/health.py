from __future__ import annotations

import time
import asyncio
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from ...core.auth import get_current_user
from ...core.config import settings
from ...services.openai_client import oai_client

router = APIRouter(prefix="/health", tags=["health"])

# ---- uptime tracking (monotonic for accuracy) ----
START_MONO = time.monotonic()
START_WALL = time.time()

# ---- probe cache to avoid hammering GPT ----
_PROBE_LOCK = asyncio.Lock()
_PROBE_TTL_SEC = 30  # cache probe result for this many seconds
_probe_cached: Dict[str, Any] = {
    "ok": None,                # bool | None
    "latency_ms": None,        # float | None
    "error": None,             # str | None
    "probed_at": None,         # float (epoch seconds) | None
}

async def _probe_gpt(timeout_sec: float = 5.0) -> Dict[str, Any]:
    """
    Minimal/cheap chat completion to verify Azure OpenAI reachability.
    Uses a tiny prompt and max_tokens=1. Cached for _PROBE_TTL_SEC.
    """
    # Return cached if fresh
    now = time.time()
    if (
        _probe_cached["probed_at"] is not None
        and (now - _probe_cached["probed_at"]) < _PROBE_TTL_SEC
        and _probe_cached["ok"] is not None
    ):
        return _probe_cached

    async with _PROBE_LOCK:
        # Double-check inside lock (another coroutine may have updated it)
        now = time.time()
        if (
            _probe_cached["probed_at"] is not None
            and (now - _probe_cached["probed_at"]) < _PROBE_TTL_SEC
            and _probe_cached["ok"] is not None
        ):
            return _probe_cached

        start = time.perf_counter()
        ok, err = True, None
        latency_ms: Optional[float] = None

        try:
            async def _call():
                # Tiny, deterministic probe; cost ~1 token completion
                return await oai_client.chat.completions.create(
                    model=settings.DEPLOYMENT,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=1,
                    temperature=0.0,
                )

            await asyncio.wait_for(_call(), timeout=timeout_sec)
            latency_ms = round((time.perf_counter() - start) * 1000.0, 1)

        except asyncio.TimeoutError:
            ok, err = False, f"timeout_after_{timeout_sec}s"
            latency_ms = round((time.perf_counter() - start) * 1000.0, 1)
        except Exception as e:
            ok, err = False, type(e).__name__

        _probe_cached.update({
            "ok": ok,
            "latency_ms": latency_ms,
            "error": err,
            "probed_at": time.time(),
        })
        return _probe_cached

def _fmt_uptime() -> dict:
    elapsed = time.monotonic() - START_MONO
    mins, secs = divmod(int(elapsed), 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)
    return {
        "seconds": round(elapsed, 3),
        "human": f"{days}d {hrs}h {mins}m {secs}s"
    }

@router.get("")
def liveness():
    """Basic liveness for load balancers/monitors. No external calls."""
    return {"status": "healthy"}

@router.get("/secure")
def liveness_secure(user=Depends(get_current_user)):
    """Liveness + JWT check."""
    return {"status": "authenticated", "user": user["username"]}

@router.get("/full")
async def readiness(request: Request, user: dict | None = Depends(get_current_user, use_cache=True)):
    """
    Readiness: uptime + cached Azure GPT probe.
    - Cheap, fast; avoids provider spam via TTL cache.
    - Adds req_id for easy correlation with access/audit logs.
    """
    req_id = getattr(request.state, "request_id", None)
    probe = await _probe_gpt()

    payload = {
        "status": "ready" if probe["ok"] else "degraded",
        "version": getattr(settings, "API_VERSION_STR", "unknown"),
        "uptime": _fmt_uptime(),
        "time_started_unix": int(START_WALL),
        "request_id": req_id,
        "gpt": {
            "ok": probe["ok"],
            "latency_ms": probe["latency_ms"],
            "error": probe["error"],
            "probed_at_unix": int(probe["probed_at"]) if probe["probed_at"] else None,
            "cache_ttl_sec": _PROBE_TTL_SEC,
            "deployment": settings.DEPLOYMENT,
            "endpoint": settings.ENDPOINT,
        },
    }

    if user:
        payload["auth"] = {"authenticated": True, "user": user["username"]}
    else:
        payload["auth"] = {"authenticated": False}

    # Consider non-200 if GPT not OK (useful for orchestrators that check /full)
    if not probe["ok"]:
        raise HTTPException(status_code=503, detail=payload)

    return payload
