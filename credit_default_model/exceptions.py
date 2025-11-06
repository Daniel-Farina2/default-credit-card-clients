class ModelError(Exception):
    """Base exception for model-related failures."""


class ValidationError(ModelError):
    """Raised when input payload does not satisfy model requirements."""

