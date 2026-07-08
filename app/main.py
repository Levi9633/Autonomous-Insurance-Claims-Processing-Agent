"""
FastAPI application entry point for the Autonomous Insurance Claims Processing Agent.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from app.routes import router

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Application Initialization
# ─────────────────────────────────────────────

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Static Files and Templates
# ─────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent

# Mount static files (CSS, JS)
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Jinja2 templates
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# ─────────────────────────────────────────────
# Include API Router
# ─────────────────────────────────────────────

app.include_router(router, prefix="", tags=["Claims Processing"])

# ─────────────────────────────────────────────
# Frontend Route
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request) -> HTMLResponse:
    """Serve the main frontend application."""
    return templates.TemplateResponse("index.html", {"request": request})


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": APP_TITLE,
        "version": APP_VERSION,
    }


# ─────────────────────────────────────────────
# Startup / Shutdown Events
# ─────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    logger.info(f"✓ {APP_TITLE} v{APP_VERSION} started successfully.")
    logger.info("✓ API available at http://localhost:8000")
    logger.info("✓ API docs available at http://localhost:8000/api/docs")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info(f"{APP_TITLE} shutting down.")
