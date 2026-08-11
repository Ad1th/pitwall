"""
PITWALL API v1 Router Aggregator.
"""

from fastapi import APIRouter
from backend.app.api.v1.races import router as races_router
from backend.app.api/v1.simulations import router as simulations_router

api_v1_router = APIRouter()
api_v1_router.include_router(races_router, prefix="/races", tags=["races"])
api_v1_router.include_router(simulations_router, tags=["simulations"])
