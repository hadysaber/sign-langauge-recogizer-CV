"""
Script for automated dataset collection using the exact feature mappings.
"""

import cv2
import numpy as np
import sys
import logging
from pathlib import Path

# Ensure this accesses the root module correctly when run directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ACTIONS, NO_SEQUENCES, SEQUENCE_LENGTH, EXTRACTED_DATA_DIR
from src.extract import mediapipe_detection, extract_keypoints, mp_holistic
from src.ui import draw_styled_landmarks, draw_collection_header

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def capture_data() -> None:
    """
    Loops through all specified actions, capturing sequences of frames for each gesture via webcam,
    extracts the landmarks, and saves them locally as .npy files.
    """
    # 1. Setup folders using pathlib
    for action in ACTIONS:
        for sequence in range(NO_SEQUENCES):
            target_dir = EXTRACTED_DATA_DIR / action / str(sequence)
            target_dir.mkdir(parents=True, exist_ok=True)

    # 2. Camera setup check
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Failed to open physical webcam device.")
        return
    
    # 3. MediaPipe Holistic Model setup
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        for action in ACTIONS:
            for sequence in range(NO_SEQUENCES):
                for frame_num in range(SEQUENCE_LENGTH):
                    ret, frame = cap.read()
                    if not ret:
                        logging.warning(f"Failed to capture frame during {action} sequence {sequence}.")
                        break

                    # Detection and extraction
                    image, results = mediapipe_detection(frame, holistic)
                    draw_styled_landmarks(image, results)
                    
                    # UI feedback via ui.py abstraction
                    is_start = (frame_num == 0)
                    draw_collection_header(image, action, sequence, is_starting=is_start)
                    
                    cv2.imshow('OpenCV Dataset Collection Feed', image)
                    if is_start:
                        cv2.waitKey(2000) # Give user a 2-second buffer to get ready
                    
                    # Export keypoints to Data Directory
                    keypoints = extract_keypoints(results)
                    npy_path = EXTRACTED_DATA_DIR / action / str(sequence) / f"{frame_num}.npy"
                    np.save(str(npy_path), keypoints)

                    # Elegant exit condition
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        logging.info("Collection interrupted by user.")
                        cap.release()
                        cv2.destroyAllWindows()
                        return
                    
    cap.release()
    cv2.destroyAllWindows()
    logging.info("Data collection completed successfully!")

if __name__ == '__main__':
    capture_data()
