"""Image decoding helpers for uploaded camera frames."""

import cv2
import numpy as np


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decodes uploaded image bytes into an OpenCV BGR frame.

    Raises:
        ValueError: If the bytes cannot be decoded as an image.
    """
    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Uploaded file could not be decoded as an image frame.")
    return frame
