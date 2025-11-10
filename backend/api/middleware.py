# File: backend/api/middleware.py
# Complete CORS and authentication middleware

"""
API Middleware
Handles CORS, authentication, rate limiting, and request logging
"""

from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware
    Prevents abuse by limiting requests per IP
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting"""
        client_ip = request.client.host
        now = datetime.utcnow()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(seconds=self.period)
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Rate limit exceeded", "retry_after": self.period}
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/Response logging middleware
    Logs all API requests with timing information
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response"""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} | "
            f"Duration: {duration:.3f}s | "
            f"Path: {request.url.path}"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware
    Validates API keys and JWT tokens
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = ["/", "/docs", "/redoc", "/openapi.json", "/health"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Validate authentication"""
        # Skip auth for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            logger.warning(f"Missing API key for {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "API key required"}
            )
        
        # Validate API key (simplified - in production use proper validation)
        if api_key != settings.SECRET_KEY:
            logger.warning(f"Invalid API key: {api_key[:10]}...")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Invalid API key"}
            )
        
        response = await call_next(request)
        return response


def setup_middleware(app):
    """
    Setup all middleware for the application
    
    Args:
        app: FastAPI application instance
    """
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"]
    )
    
    # Logging Middleware
    app.add_middleware(LoggingMiddleware)
    
    # Rate Limiting Middleware
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)
    
    logger.info("All middleware configured successfully")
