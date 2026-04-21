"""
Real-time Sign Language Recognition Interface
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    import cv2
    import numpy as np
    import mediapipe as mp
    import tensorflow as tf
except ImportError as e:
    logging.error(f"Missing critical dependency: {e.name}. Please ensure you run 'pip install -r requirements.txt'")
    sys.exit(1)

from collections import deque
from pathlib import Path

from src.config import ACTIONS, MODEL_PATH, CONFIDENCE_THRESHOLD, SEQUENCE_LENGTH
from src.extract import mp_holistic, mediapipe_detection, extract_keypoints
from src.model import create_lstm_model
from src.ui import draw_styled_landmarks, draw_presentation_overlay
from src.smoothing import PredictionSmoother

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
        
    # 2. Setup Temporal Buffers & State Mechanics
    sequence = deque(maxlen=SEQUENCE_LENGTH) 
    smoother = PredictionSmoother(window_size=5)
    
    current_action = ""
    confidence = 0.0
    status_text = "Waiting for sequence..."
    smoothing_active = True

    # 3. Setup Hardware Interface
    cap = cv2.VideoCapture(0)
    # Give the app a 16:9 widescreen rendering baseline if supported by hardware
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        logging.error("Failed to grab physical webcam frame. Check your camera driver.")
        return
        
    logging.info("Opening Webcam... Press 'q' to quit.")
    
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            start_tick = cv2.getTickCount()
            
            ret, frame = cap.read()
            if not ret:
                logging.warning("Dropped frame. Skipping...")
                continue
                
            # Computer Vision feature extraction
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)
            
            # Logic: Hands check (Core upgrade for stability)
            has_hands = bool(results.left_hand_landmarks or results.right_hand_landmarks)
            
            if not has_hands:
                status_text = "No hands detected"
                sequence.clear()
            else:
                # Format and Buffer keypoints
                keypoints = extract_keypoints(results)
                sequence.append(keypoints)

                if len(sequence) < SEQUENCE_LENGTH:
                    status_text = "Waiting for sequence..."
                else:
                    status_text = "Predicting"
                    
                    # Shape context: (1, 30, 258)
                    res = model.predict(np.expand_dims(list(sequence), axis=0), verbose=0)[0]
                    prediction_idx = int(np.argmax(res))
                    
                    if res[prediction_idx] > CONFIDENCE_THRESHOLD:
                        raw_action = ACTIONS[prediction_idx]
                        confidence = float(res[prediction_idx])
                        
                        # Apply consensus smoothing
                        if smoothing_active:
                            smoother.add_prediction(raw_action)
                            stable_action = smoother.get_stable_prediction()
                            if stable_action:
                                current_action = stable_action
                        else:
                            current_action = raw_action
                            
            # Calculate metrics
            fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - start_tick))
            
            # Render full graduation-demo UI
            draw_presentation_overlay(image, status_text, current_action, confidence, fps, smoothing_active)
            
            cv2.imshow('Sign Language AI Inference Core', image)
            
            # Interactive Keyboard Listeners
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                logging.info("Inference shutdown triggered by user.")
                break
            elif key == ord('r'):
                logging.info("User forced sequence reset.")
                sequence.clear()
                smoother.reset()
                current_action = ""
            elif key == ord('s'):
                smoothing_active = not smoothing_active
                logging.info(f"Smoothing toggled to: {smoothing_active}")
                smoother.reset()
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    on_screen_prediction()
