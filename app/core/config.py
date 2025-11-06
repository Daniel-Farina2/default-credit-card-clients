import os
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application configuration container."""

    base_dir: Path = Field(
        default=Path(__file__).resolve().parents[2],
        description="Project root directory.",
    )
    api_title: str = Field(
        default=os.getenv("API_TITLE", "Default Credit Risk API"),
        description="FastAPI application title.",
    )
    api_version: str = Field(
        default=os.getenv("API_VERSION", "0.1.0"),
        description="FastAPI application version.",
    )
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Root logging level.",
    )
    max_batch_rows: int = Field(
        default=int(os.getenv("MAX_BATCH_ROWS", "60000")),
        description="Upper bound for accepted batch rows.",
    )


settings = Settings()

