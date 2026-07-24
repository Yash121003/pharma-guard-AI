"""
Database initialization.

Imports every ORM model so they register on Base.metadata, then creates
any missing tables. Real projects should use Alembic migrations for
anything beyond local dev bootstrap -- this is intentionally only used
on app startup for convenience (see app/main.py).
"""
import logging

from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    # Model imports are deferred to here (rather than at module load time)
    # so Base.metadata is fully populated before create_all runs. Each
    # import is independent so this stays safe to call even in early
    # phases before every model module exists yet.
    import importlib

    for module_name in ("user", "product", "batch", "complaint", "ai_conversation", "audit_log"):
        try:
            importlib.import_module(f"app.models.{module_name}")
        except ModuleNotFoundError:
            logger.debug("Model module app.models.%s not present yet, skipping.", module_name)

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured (create_all complete). Tables: %s", list(Base.metadata.tables.keys()))
