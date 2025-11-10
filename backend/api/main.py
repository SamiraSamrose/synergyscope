# File: backend/api/main.py

"""
FastAPI Main Application
Core API server with routing and middleware
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger
from backend.api.routes import router

settings = get_settings()
logger = setup_logger(__name__, settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Agents for Team Adaptation, Meta Evolution and Collaborative Growth",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "../../frontend/static")
templates_path = os.path.join(os.path.dirname(__file__), "../../frontend/templates")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

if os.path.exists(templates_path):
    templates = Jinja2Templates(directory=templates_path)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"API available at http://{settings.API_HOST}:{settings.API_PORT}")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)

# Root endpoint
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    if os.path.exists(templates_path):
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse(content="<h1>SynergyScope API</h1><p>Visit /docs for API documentation</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1
    )