"""Security middleware for permissions and rate limiting."""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from divyadrishti.security.rate_limit import InMemoryRateLimiter
from divyadrishti.security.token import decode_token

PUBLIC_PATHS = {
    "/api/v1/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/verify-email",
    "/api/v1/auth/request-password-reset",
    "/api/v1/auth/reset-password",
}

_rate_limiter = InMemoryRateLimiter()


class PermissionMiddleware(BaseHTTPMiddleware):
    """Middleware that validates JWTs, sets request state, and enforces rate limits."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Rate limit by IP
        client_ip = request.client.host if request.client else "unknown"
        if not _rate_limiter.allow(client_ip):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})

        # Skip authentication for public paths
        if any(path.startswith(public) for public in PUBLIC_PATHS):
            return await call_next(request)

        # Set current user from token if available
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[7:]
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                request.state.user_id = payload.get("sub")

        return await call_next(request)
