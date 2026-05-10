from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication and authorization."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Public endpoints that don't require authentication
        self.public_endpoints = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/register",
            "/auth/login",
            "/auth/refresh",
            "/auth/google/url",
            "/auth/facebook/url",
            "/auth/google/callback",
            "/auth/facebook/callback",
            "/auth/signupwithgoogle",
            "/auth/signupwithfacebook"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in self.public_endpoints:
            return await call_next(request)
        
        # Check for authentication header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
        
        # Continue with the request
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app: ASGIApp, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                timestamp for timestamp in self.clients[client_ip]
                if current_time - timestamp < self.period
            ]
        else:
            self.clients[client_ip] = []
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Add current request
        self.clients[client_ip].append(current_time)
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
        
        return response
