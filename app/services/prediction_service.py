"""Prediction service responsible for orchestrating model inference."""

from __future__ import annotations

import asyncio
import io
import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from app.core.config import settings
from credit_default_model import (
    CreditDefaultModel,
    ModelError,
    ValidationError as ModelValidationError,
)

LOGGER = logging.getLogger(__name__)


class PredictionError(Exception):
    """Domain exception raised on invalid prediction inputs."""


class PredictionService:
    """High-level orchestration for scoring requests."""

    def __init__(self) -> None:
        """Instantiate the model wrapper."""

        self._model = CreditDefaultModel()
        LOGGER.info(
            "PredictionService initialised using threshold %.4f", self.threshold
        )

    @property
    def threshold(self) -> float:
        """Return the probability threshold for positive classification."""

        return self._model.threshold

    async def predict_single(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Predict default probability for a single applicant.

        Args:
            payload: Applicant data provided by the caller.

        Returns:
            Dictionary containing probability, threshold, default flag, and id.

        Raises:
            PredictionError: When the payload fails validation.
        """

        frame = pd.DataFrame([payload])
        try:
            scored = await asyncio.to_thread(self._model.score, frame)
        except ModelValidationError as exc:
            raise PredictionError(str(exc)) from exc
        except ModelError:
            LOGGER.exception("Model failed to process single payload.")
            raise

        row = scored.iloc[0]
        result = {
            "probability": float(row["probability"]),
            "is_default": bool(row["is_default"]),
            "threshold": self.threshold,
        }
        if "id" in row and pd.notna(row["id"]):
            result["id"] = str(row["id"])
        return result

    async def predict_batch(self, file_bytes: bytes, filename: str) -> pd.DataFrame:
        """Predict default probabilities for a batch payload.

        Args:
            file_bytes: Raw bytes of the uploaded file.
            filename: Original file name used to detect format.

        Returns:
            DataFrame with id, probability, and is_default columns.

        Raises:
            PredictionError: When the file exceeds limits or fails validation.
        """

        dataframe = self._read_input_file(file_bytes, filename)
        if len(dataframe) > settings.max_batch_rows:
            raise PredictionError(
                f"Batch size {len(dataframe)} exceeds limit of {settings.max_batch_rows} rows."
            )
        try:
            scored = await asyncio.to_thread(self._model.score, dataframe)
        except ModelValidationError as exc:
            raise PredictionError(str(exc)) from exc
        except ModelError:
            LOGGER.exception("Model failed to process batch payload.")
            raise
        return scored.reset_index(drop=True)

    @staticmethod
    def _read_input_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
        """Parse CSV or XLS batch files into a pandas DataFrame.

        Args:
            file_bytes: Raw bytes of the uploaded file.
            filename: Original file name used to detect format.

        Returns:
            DataFrame parsed from the uploaded payload.

        Raises:
            PredictionError: If the file type is not supported.
        """

        extension = Path(filename).suffix.lower()
        if extension == ".csv":
            return pd.read_csv(io.BytesIO(file_bytes))
        if extension == ".xls":
            return pd.read_excel(io.BytesIO(file_bytes))
        raise PredictionError("Only CSV and XLS files are supported.")


_SERVICE_INSTANCE: PredictionService | None = None


def get_prediction_service() -> PredictionService:
    """Return a singleton instance of the PredictionService."""

    global _SERVICE_INSTANCE
    if _SERVICE_INSTANCE is None:
        _SERVICE_INSTANCE = PredictionService()
    return _SERVICE_INSTANCE
