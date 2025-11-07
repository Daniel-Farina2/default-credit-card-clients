import os
from pathlib import Path
from pydantic import BaseModel, Field


def _default_model_dir() -> Path:
    """Return the default directory that stores model artifacts."""

    override = os.getenv("MODEL_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[1] / "models"


class ModelSettings(BaseModel):
    """Model artifact configuration."""

    base_dir: Path = Field(
        default=Path(__file__).resolve().parents[1],
        description="Repository root directory.",
    )
    model_dir: Path = Field(
        default_factory=_default_model_dir,
        description="Directory containing serialized model artifacts.",
    )
    model_filename: str = Field(
        default=os.getenv("MODEL_FILENAME", "cat_model_v1.0.0.pkl"),
        description="Cloudpickle artifact that stores the trained estimator.",
    )
    input_signature_filename: str = Field(
        default=os.getenv(
            "MODEL_SIGNATURE", "cat_model_v1.0.0_input_signature.json"
        ),
        description="JSON file describing required input schema.",
    )
    metadata_filename: str = Field(
        default=os.getenv("MODEL_METADATA", "cat_model_v1.0.0_metadata.json"),
        description="JSON file containing metadata (metrics, threshold).",
    )
    id_column_name: str = Field(
        default=os.getenv("MODEL_ID_COLUMN", "ID"),
        description="Identifier column name used in inference payloads.",
    )

    @property
    def model_path(self) -> Path:
        """Return the fully qualified path to the serialized estimator."""

        return self.model_dir / self.model_filename

    @property
    def signature_path(self) -> Path:
        """Return the path to the input signature JSON."""

        return self.model_dir / self.input_signature_filename

    @property
    def metadata_path(self) -> Path:
        """Return the path to the metadata JSON."""

        return self.model_dir / self.metadata_filename


model_settings = ModelSettings()
