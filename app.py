"""
Real-time Sign Language Recognition Interface
"""

import cv2
import numpy as np
import logging
from collections import deque
from pathlib import Path

from src.config import ACTIONS, MODEL_PATH, CONFIDENCE_THRESHOLD, SEQUENCE_LENGTH
from src.extract import mp_holistic, mediapipe_detection, extract_keypoints
from src.model import create_lstm_model
from src.ui import draw_styled_landmarks, draw_inference_overlay

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def on_screen_prediction() -> None:
    """
    Initializes the hardware webcam interface, loads the LSTM sequence weights, 
    and handles the main real-time inference loop safely.
    """
    # 1. Initialize and Load LSTM Model
    model = create_lstm_model()
    if Path(MODEL_PATH).exists():
        model.load_weights(str(MODEL_PATH))
        logging.info("Model loaded successfully.")
    else:
        logging.warning(f"File not found at '{MODEL_PATH}'. Running with uninitialized random weights.")
        
    # 2. Setup Temporal Buffer
    # Automatically manages memory by dropping the oldest frame
    sequence = deque(maxlen=SEQUENCE_LENGTH) 
    
    # 3. Setup Hardware Interface
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Failed to grab physical webcam frame. Check your camera driver.")
        return
    
    current_action = "Waiting..."
    confidence = 0.0

    logging.info("Opening Webcam... Press 'q' to quit.")
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.warning("Dropped frame. Skipping...")
                continue
                
            # Computer Vision feature extraction
            image, results = mediapipe_detection(frame, holistic)
            
            # Isolated UI abstraction
            draw_styled_landmarks(image, results)
            
            # Format and Buffer keypoints
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            
            # Predict only if we have a full buffer sequence
            if len(sequence) == SEQUENCE_LENGTH:
                # Shape context: (1, 30, 258)
                res = model.predict(np.expand_dims(list(sequence), axis=0), verbose=0)[0]
                prediction_idx = int(np.argmax(res))
                
                # Filter by system confidence threshold
                if res[prediction_idx] > CONFIDENCE_THRESHOLD:
                    current_action = ACTIONS[prediction_idx]
                    confidence = float(res[prediction_idx])
            
            # Render UI overlay via abstraction
            draw_inference_overlay(image, current_action, confidence)
            
            cv2.imshow('Sign Language AI Inference Core', image)
            
            if cv2.waitKey(10) & 0xFF == ord('q'):
                logging.info("Inference shutdown triggered by user.")
                break
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    on_screen_prediction()
