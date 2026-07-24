"""
Aggregates all v1 API routers.
"""
from fastapi import APIRouter

from app.api.v1 import ai, auth, complaints, uploads

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(complaints.router, prefix="/complaints", tags=["complaints"])
router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
