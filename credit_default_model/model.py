import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import cloudpickle
import pandas as pd
from .config import ModelSettings, model_settings
from .exceptions import ModelError, ValidationError

LOGGER = logging.getLogger(__name__)


class CreditDefaultModel:
    """Encapsulates artifact loading, validation, and scoring logic."""

    def __init__(self, settings: ModelSettings | None = None) -> None:
        """Initialise the model with the provided settings.

        Args:
            settings: Optional model configuration overrides.
        """

        self._settings = settings or model_settings
        self._estimator = self._load_estimator(self._settings.model_path)
        self._signature = self._load_json(self._settings.signature_path)
        self._metadata = self._load_json(self._settings.metadata_path)
        self._expected_columns = self._signature.get("expected_columns", [])
        self._dtype_map: Dict[str, str] = self._signature.get("dtypes", {})

        metadata_threshold = self._metadata.get("threshold")

        if metadata_threshold is None:
            raise ModelError("Model metadata does not declare a probability threshold.")
        self._threshold: float = float(metadata_threshold)

        self._id_column = (
            self._signature.get("id_name") or self._settings.id_column_name
        )

        LOGGER.info(
            "Loaded credit default model with %d features, ID column '%s', threshold %.4f",
            len(self._expected_columns),
            self._id_column,
            self._threshold,
        )

    @property
    def threshold(self) -> float:
        """Return the default probability threshold."""

        return self._threshold

    @property
    def id_column(self) -> str:
        """Return the identifier column name."""

        return self._id_column

    @property
    def expected_columns(self) -> list[str]:
        """Return the ordered list of expected feature names."""

        return list(self._expected_columns)

    def predict_proba(self, frame: pd.DataFrame) -> pd.Series:
        """Return positive class probabilities for the provided dataframe.

        Args:
            frame: Input rows containing identifier and feature columns.

        Returns:
            Series with probabilities indexed by the input rows.
        """

        features, _ = self._prepare_features(frame)
        probabilities = self._predict_proba(features)
        return pd.Series(probabilities, index=features.index, name="probability")

    def score(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Return probabilities and default flags for the provided dataframe.

        Args:
            frame: Input rows containing identifier and feature columns.

        Returns:
            DataFrame with id, probability, and is_default columns.
        """

        features, identifiers = self._prepare_features(frame)
        probabilities = self._predict_proba(features)
        result = pd.DataFrame(
            {
                "id": identifiers.astype(str),
                "probability": probabilities,
            },
            index=features.index,
        )
        result["is_default"] = result["probability"] >= self._threshold
        return result

    def _prepare_features(self, frame: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Validate and coerce the payload before scoring.

        Args:
            frame: Raw payload supplied by the caller.

        Returns:
            Tuple of (features dataframe, identifier series).

        Raises:
            ValidationError: If the payload does not satisfy schema requirements.
        """

        if self._id_column not in frame.columns:
            raise ValidationError(f"Missing identifier column: {self._id_column}.")
        if "default" in frame.columns:
            raise ValidationError(
                "Column 'default' is not allowed in inference payloads."
            )

        missing = [col for col in self._expected_columns if col not in frame.columns]
        if missing:
            raise ValidationError(f"Missing columns: {', '.join(missing)}.")

        extra = [
            col
            for col in frame.columns
            if col not in self._expected_columns and col != self._id_column
        ]
        if extra:
            LOGGER.debug("Ignoring extra columns: %s", ", ".join(extra))

        features = frame[self._expected_columns].copy()
        features = features.replace(r"^\s*$", pd.NA, regex=True)
        for column, dtype in self._dtype_map.items():
            if column not in features.columns:
                continue
            if dtype.startswith("int"):
                features[column] = pd.to_numeric(
                    features[column], errors="raise"
                ).astype("int64")
            elif dtype.startswith("float"):
                features[column] = pd.to_numeric(
                    features[column], errors="raise"
                ).astype("float64")
            elif dtype == "category":
                features[column] = features[column].astype("category")
            else:
                raise ValidationError(
                    f"Unsupported dtype '{dtype}' for column '{column}'."
                )

        if features.isnull().any(axis=1).any():
            raise ValidationError("Input payload contains missing values.")

        identifiers = frame[self._id_column]
        if identifiers.isnull().any():
            raise ValidationError("Identifier column contains missing values.")

        return features, identifiers.astype(str)

    def _predict_proba(self, features: pd.DataFrame) -> pd.Series:
        """Predict positive class probabilities from prepared features.

        Args:
            features: Prepared feature matrix.

        Returns:
            Series with positive-class probabilities.

        Raises:
            ModelError: If the estimator does not expose binary probabilities.
        """

        probabilities = self._estimator.predict_proba(features)
        return pd.Series(probabilities[:, 1], index=features.index, name="probability")

    @staticmethod
    def _load_estimator(path: Path):
        """Load the serialized estimator from disk.

        Args:
            path: Location of the serialized model artifact.

        Returns:
            Loaded estimator instance.

        Raises:
            ModelError: If the artifact cannot be located.
        """

        if not path.exists():
            raise ModelError(f"Estimator artifact not found at {path}.")
        LOGGER.debug("Loading estimator from %s", path)
        with path.open("rb") as stream:
            return cloudpickle.load(stream)

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        """Load JSON artifact from disk.

        Args:
            path: Location of the JSON file.

        Returns:
            Parsed JSON payload.

        Raises:
            ModelError: If the artifact cannot be located.
        """

        if not path.exists():
            raise ModelError(f"JSON artifact not found at {path}.")
        return json.loads(path.read_text(encoding="utf-8"))


def load_model(settings: ModelSettings | None = None) -> CreditDefaultModel:
    """Return a ready-to-use model instance.

    Args:
        settings: Optional model configuration overrides.

    Returns:
        Instantiated CreditDefaultModel.
    """

    return CreditDefaultModel(settings=settings)
