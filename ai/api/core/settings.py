"""
Runtime settings for the FastAPI recognition backend.

These settings intentionally read from the existing AI config module so the
backend stays aligned with the training and desktop inference pipeline.
"""

from pydantic import BaseModel, ConfigDict

from src.config import (
    ACTIONS,
    BEST_MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    LABEL_MAP_PATH,
    MODEL_METADATA_PATH,
    MODEL_PATH,
    NORMALIZE_LANDMARKS,
    SEQUENCE_LENGTH,
)


class ApiSettings(BaseModel):
    """Typed settings exposed to API services."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    app_name: str = "Sign Language Translator API"
    api_prefix: str = "/api/v1"
    model_path: str = str(BEST_MODEL_PATH if BEST_MODEL_PATH.exists() else MODEL_PATH)
    fallback_model_path: str = str(MODEL_PATH)
    label_map_path: str = str(LABEL_MAP_PATH)
    model_metadata_path: str = str(MODEL_METADATA_PATH)
    actions: list[str] = ACTIONS
    sequence_length: int = SEQUENCE_LENGTH
    confidence_threshold: float = CONFIDENCE_THRESHOLD
    normalize_landmarks: bool = NORMALIZE_LANDMARKS
    smoothing_window_size: int = 5
    mediapipe_detection_confidence: float = 0.5
    mediapipe_tracking_confidence: float = 0.5


settings = ApiSettings()
