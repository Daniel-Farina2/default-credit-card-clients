from fastapi import APIRouter
from .controllers.prediction_controller import router as prediction_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(prediction_router, tags=["predictions"])

