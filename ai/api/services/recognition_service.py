"""
Stateful recognition service used by the FastAPI prediction endpoint.

The service keeps a rolling 30-frame landmark buffer, matching the desktop
OpenCV inference app. For Phase 2 this is intentionally a local singleton
service; later mobile sessions can be separated by client/session id.
"""

import json
import logging
from collections import deque
from pathlib import Path
from typing import Any

import mediapipe as mp
import numpy as np
import tensorflow as tf

from api.core.settings import ApiSettings, settings
from api.schemas.prediction_schema import PredictionResponse
from src.dataset import normalize_sequence
from src.extract import extract_keypoints, mediapipe_detection
from src.smoothing import PredictionSmoother

logger = logging.getLogger(__name__)


class RecognitionService:
    """Runs MediaPipe landmark extraction and Keras sign classification."""

    def __init__(self, api_settings: ApiSettings = settings) -> None:
        self.settings = api_settings
        self.sequence: deque[np.ndarray] = deque(maxlen=api_settings.sequence_length)
        self.smoother = PredictionSmoother(
            window_size=api_settings.smoothing_window_size
        )
        self.history: deque[str] = deque(maxlen=20)
        self.current_label = ""
        self.current_confidence = 0.0
        self.model = self._load_model()
        self.actions = self._load_actions()
        self.holistic = mp.solutions.holistic.Holistic(
            min_detection_confidence=api_settings.mediapipe_detection_confidence,
            min_tracking_confidence=api_settings.mediapipe_tracking_confidence,
        )

    def _load_model(self) -> tf.keras.Model:
        """Loads the best available Keras model."""
        model_path = Path(self.settings.model_path)
        if not model_path.exists():
            model_path = Path(self.settings.fallback_model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                "No trained model found. Run src/train.py before starting the API."
            )

        logger.info("Loading sign recognition model from %s", model_path)
        return tf.keras.models.load_model(str(model_path))

    def _load_actions(self) -> list[str]:
        """Loads labels in model output order."""
        label_map_path = Path(self.settings.label_map_path)
        if not label_map_path.exists():
            logger.warning("Label mapping missing; falling back to config ACTIONS.")
            return self.settings.actions

        with open(label_map_path, "r") as file:
            label_map: dict[str, int] = json.load(file)
        return [
            label for label, _ in sorted(label_map.items(), key=lambda item: item[1])
        ]

    def reset(self) -> None:
        """Clears sequence and smoothing state."""
        self.sequence.clear()
        self.smoother.reset()
        self.history.clear()
        self.current_label = ""
        self.current_confidence = 0.0

    def close(self) -> None:
        """Releases MediaPipe resources."""
        self.holistic.close()

    def predict(self, frame_bgr: np.ndarray) -> PredictionResponse:
        """Processes one BGR camera frame and returns the latest prediction state."""
        _, results = mediapipe_detection(frame_bgr, self.holistic)
        has_hands = bool(results.left_hand_landmarks or results.right_hand_landmarks)

        if not has_hands:
            self.sequence.clear()
            self.smoother.reset()
            return PredictionResponse(
                label=self.current_label,
                confidence=self.current_confidence,
                stable=False,
                history=list(self.history),
            )

        self.sequence.append(extract_keypoints(results).astype(np.float32))

        if len(self.sequence) < self.settings.sequence_length:
            return PredictionResponse(
                label=self.current_label,
                confidence=self.current_confidence,
                stable=False,
                history=list(self.history),
            )

        model_input = np.array(list(self.sequence), dtype=np.float32)
        if self.settings.normalize_landmarks:
            model_input = normalize_sequence(model_input)

        probabilities = self.model.predict(
            np.expand_dims(model_input, axis=0),
            verbose=0,
        )[0]
        prediction_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[prediction_idx])

        if confidence < self.settings.confidence_threshold:
            return PredictionResponse(
                label=self.current_label,
                confidence=confidence,
                stable=False,
                history=list(self.history),
            )

        raw_label = self.actions[prediction_idx]
        self.smoother.add_prediction(raw_label)
        stable_label = self.smoother.get_stable_prediction()

        stable = stable_label is not None
        if stable_label:
            self.current_label = stable_label
            self.current_confidence = confidence
            if not self.history or self.history[-1] != stable_label:
                self.history.append(stable_label)

        return PredictionResponse(
            label=self.current_label,
            confidence=confidence,
            stable=stable,
            history=list(self.history),
        )


recognition_service: RecognitionService | None = None


def get_recognition_service() -> RecognitionService:
    """Returns the singleton recognition service, creating it lazily."""
    global recognition_service
    if recognition_service is None:
        recognition_service = RecognitionService()
    return recognition_service


def shutdown_recognition_service() -> None:
    """Closes the singleton recognition service if it was created."""
    global recognition_service
    if recognition_service is not None:
        recognition_service.close()
        recognition_service = None
