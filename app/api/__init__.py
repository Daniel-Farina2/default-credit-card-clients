from fastapi import APIRouter
from .v1.router import api_v1_router

api_router = APIRouter()
api_router.include_router(api_v1_router)

__all__ = ["api_router"]

