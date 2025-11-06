from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import api_router
from app.core import settings, setup_logging
from app.services import get_prediction_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Configure logging and warm up the prediction service."""

    setup_logging()
    get_prediction_service()
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    """Return a simple heartbeat."""

    return {"status": "ok"}
