import sys
import os
import uuid
import time
import httpx
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from shared.logging.structured import get_logger, request_id_ctx
from shared.cache.redis_client import cache
from shared.errors.handlers import (
    api_exception_handler, http_exception_handler, validation_exception_handler,
    generic_exception_handler, APIException
)
from fastapi.exceptions import RequestValidationError

logger = get_logger("api-gateway")

app = FastAPI(title="TravelMind AI - API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Service URLs from Environment or Container Defaults
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
TRIP_SERVICE_URL = os.getenv("TRIP_SERVICE_URL", "http://trip-service:8000")
RECOMMENDATION_SERVICE_URL = os.getenv("RECOMMENDATION_SERVICE_URL", "http://recommendation-service:8000")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")
PREDICTION_SERVICE_URL = os.getenv("PREDICTION_SERVICE_URL", "http://prediction-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")

SERVICE_MAP = {
    "/api/auth": USER_SERVICE_URL,
    "/api/users": USER_SERVICE_URL,
    "/api/trips": TRIP_SERVICE_URL,
    "/api/recommendations": RECOMMENDATION_SERVICE_URL,
    "/api/ai": AI_SERVICE_URL,
    "/api/predictions": PREDICTION_SERVICE_URL,
    "/api/notifications": NOTIFICATION_SERVICE_URL,
}

# ==================== MIDDLEWARES ====================
@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_ctx.set(req_id)
    
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    response.headers["X-Request-ID"] = req_id
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)"
    )
    return response

def check_rate_limit(client_ip: str, max_requests: int = 100, window_seconds: int = 60):
    """FR-20 Rate Limiting using Redis cache or memory fallback."""
    key = f"rate_limit:{client_ip}"
    current = cache.get(key) or 0
    if current >= max_requests:
        raise APIException("TOO_MANY_REQUESTS", "Too many requests. Please wait a moment before retrying.", 429)
    cache.set(key, current + 1, ttl_seconds=window_seconds)

# ==================== GATEWAY PROXY HANDLER ====================
async def proxy_request(service_base_url: str, target_path: str, request: Request) -> Response:
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    target_url = f"{service_base_url}{target_path}"
    if request.query_params:
        target_url += f"?{request.query_params}"

    headers = dict(request.headers)
    headers["X-Request-ID"] = request_id_ctx.get()
    # Remove host header to avoid SSL/Routing issues
    headers.pop("host", None)

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers)
            )
    except httpx.ConnectError:
        logger.error(f"Failed to connect to backend microservice at {target_url}")
        msg = "Authentication service is temporarily unavailable." if service_base_url == USER_SERVICE_URL else "Backend service is currently unavailable."
        raise APIException("SERVICE_UNAVAILABLE", msg, 503)
    except httpx.TimeoutException:
        logger.error(f"Timeout calling backend microservice at {target_url}")
        msg = "Authentication service timed out." if service_base_url == USER_SERVICE_URL else "Backend service timed out."
        raise APIException("GATEWAY_TIMEOUT", msg, 504)
    except Exception as exc:
        logger.error(f"Error proxying request to {target_url}: {str(exc)}")
        msg = "Authentication service is temporarily unavailable." if service_base_url == USER_SERVICE_URL else "Error communicating with upstream service."
        raise APIException("BAD_GATEWAY", msg, 502)

# ==================== ROUTES & AGGREGATION ====================
@app.get("/health")
async def health_check():
    statuses = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in [
            ("user-service", USER_SERVICE_URL),
            ("trip-service", TRIP_SERVICE_URL),
            ("recommendation-service", RECOMMENDATION_SERVICE_URL),
            ("ai-service", AI_SERVICE_URL),
            ("prediction-service", PREDICTION_SERVICE_URL),
            ("notification-service", NOTIFICATION_SERVICE_URL),
        ]:
            try:
                r = await client.get(f"{url}/health")
                statuses[name] = "healthy" if r.status_code == 200 else "degraded"
            except Exception:
                statuses[name] = "unreachable"

    all_healthy = all(s == "healthy" for s in statuses.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "api-gateway",
        "microservices": statuses
    }

# Dynamic Proxy Catch-All for /api/*
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_proxy(path: str, request: Request):
    full_path = f"/api/{path}"
    
    # Route matching
    matched_url = None
    target_service_path = full_path

    if full_path.startswith("/api/auth"):
        matched_url = USER_SERVICE_URL
        # Map /api/auth/login -> /users/login
        target_service_path = full_path.replace("/api/auth", "/users")
    elif full_path.startswith("/api/users"):
        matched_url = USER_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    elif full_path.startswith("/api/trips"):
        matched_url = TRIP_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    elif full_path.startswith("/api/bookings") or full_path.startswith("/api/invoices"):
        matched_url = TRIP_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    elif full_path.startswith("/api/recommendations"):
        matched_url = RECOMMENDATION_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    elif full_path.startswith("/api/ai"):
        matched_url = AI_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    elif full_path.startswith("/api/predictions"):
        matched_url = PREDICTION_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    elif full_path.startswith("/api/notifications"):
        matched_url = NOTIFICATION_SERVICE_URL
        target_service_path = full_path.replace("/api", "")
    else:
        raise APIException("NOT_FOUND", f"No gateway route matching '{full_path}'", 404)

    return await proxy_request(matched_url, target_service_path, request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
