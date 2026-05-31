"""Schemas for sign prediction API responses."""

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Response returned by POST /api/v1/predict."""

    label: str = Field(..., description="Stable detected sign label, or empty while waiting.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence.")
    stable: bool = Field(..., description="Whether the returned label is stable after smoothing.")
    history: list[str] = Field(default_factory=list, description="Recent stable detected labels.")
