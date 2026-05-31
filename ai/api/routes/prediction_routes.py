"""Prediction endpoints for uploaded camera frames."""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from api.schemas.prediction_schema import PredictionResponse
from api.services.recognition_service import get_recognition_service
from api.utils.image_utils import decode_image_bytes

router = APIRouter(prefix="/api/v1", tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict_sign(frame: UploadFile = File(...)) -> PredictionResponse:
    """
    Accepts one uploaded image frame and returns the current sign prediction.

    The backend keeps the rolling sequence buffer between calls, so the mobile
    app should send camera frames repeatedly while detection is active.
    """
    try:
        frame_bytes = await frame.read()
        frame_bgr = decode_image_bytes(frame_bytes)
        service = get_recognition_service()
        return service.predict(frame_bgr)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc
