"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.init_db import init_db
from app.utils.exceptions import register_exception_handlers

setup_logging()
logger = logging.getLogger(__name__)


def check_ai_configuration(app: FastAPI) -> None:
    """
    Startup check for AI configuration. Never raises/crashes the app --
    if Groq isn't configured and mock mode is off, we log a clear warning
    and let the app start normally; AI endpoints will return a clear
    502 AIProcessingError at request time instead of the whole app failing
    to boot. This is deliberate: a missing AI key shouldn't take down
    auth, complaints CRUD, or anything else that doesn't need AI.
    """
    if settings.AI_MOCK_MODE:
        app.state.ai_status = "mock"
        logger.info("AI_MOCK_MODE is enabled -- AI endpoints will return mock responses (no Groq calls).")
        return

    if not settings.GROQ_API_KEY:
        app.state.ai_status = "unconfigured"
        logger.warning(
            "GROQ_API_KEY is not set and AI_MOCK_MODE is false. AI endpoints (extract, chat, "
            "summarize, root-cause, capa, risk, duplicate-check, completeness) will fail with a "
            "clear error until you set GROQ_API_KEY in .env or set AI_MOCK_MODE=true. "
            "The rest of the application will run normally."
        )
        return

    app.state.ai_status = "live"
    logger.info("GROQ_API_KEY is configured -- AI endpoints will call the real Groq API.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s [%s]", settings.APP_NAME, settings.ENVIRONMENT)
    try:
        init_db()
    except Exception:
        logger.exception("Database initialization failed on startup.")
        raise
    check_ai_configuration(app)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered customer complaint management system for pharmaceutical manufacturing.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/", tags=["health"])
def root() -> dict:
    return {"service": settings.APP_NAME, "status": "ok"}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "ai_status": getattr(app.state, "ai_status", "unknown"),
    }


# API routers are wired up incrementally as each phase adds functionality.
# (Phase 4 adds /auth, Phase 5-ish adds /complaints, /uploads, /ai.)
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
