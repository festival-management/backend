__all__ = (
    "get_pending_statistic_router",
    "get_statistic_router",
)

from fastapi import APIRouter

from .get_pending_statistic import get_pending_statistic_router
from .get_statistic import get_statistic_router

statistics = APIRouter(prefix="/statistics", tags=["statistics"])
statistics.include_router(get_pending_statistic_router)
statistics.include_router(get_statistic_router)
