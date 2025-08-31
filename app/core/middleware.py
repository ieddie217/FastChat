import time, uuid, logging
from fastapi import Request
from starlette.responses import Response

log = logging.getLogger("access")

async def http_access_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = req_id

    method, path = request.method, request.url.path
    client_ip = request.client.host if request.client else "-"
    ua = request.headers.get("user-agent", "-")

    start = time.perf_counter()
    status = 500
    resp: Response | None = None
    try:
        resp = await call_next(request)
        status = resp.status_code
        return resp
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        if resp is not None:
            resp.headers["X-Request-ID"] = req_id
        log.info(
            f'req_id={req_id} ip={client_ip} {method} {path} '
            f'status={status} elapsed_ms={elapsed_ms:.1f} ua="{ua}"'
        )
