import cv2
import numpy as np
import os
from collections import deque

from src.config import ACTIONS, MODEL_PATH
from src.extract import mp_holistic, mediapipe_detection, draw_styled_landmarks, extract_keypoints
from src.model import create_lstm_model

def on_screen_prediction():
    """Runs the full real-time recognition pipeline."""
    # 1. Initialize and Load LSTM Model
    model = create_lstm_model()
    try:
        model.load_weights(MODEL_PATH)
        print("Model loaded perfectly.")
    except Exception as e:
        print(f"Warning: Failed to load model weights at '{MODEL_PATH}'. Running with random uninitialized weights for mock-testing. Please train first.")
        
    # 2. Setup Temporal Buffer
    # A deque automatically pops the oldest frame when maxlen is reached, maintaining a sliding window
    sequence = deque(maxlen=30) 
    
    # 3. Setup Hardware Interface
    cap = cv2.VideoCapture(0)
    
    current_action = "Waiting..."
    confidence = 0.0

    print("Opening Webcam... Press 'q' to quit.")
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab physical webcam frame. Skipping...")
                continue
                
            # Computer Vision feature extraction
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)
            
            # Format and Buffer keypoints
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            
            # Predict only if we have a full sequence (30 frames / 1s)
            if len(sequence) == 30:
                res = model.predict(np.expand_dims(list(sequence), axis=0), verbose=0)[0]
                prediction_idx = int(np.argmax(res))
                
                # Confidence Threshold Filter
                if res[prediction_idx] > 0.70:
                    current_action = ACTIONS[prediction_idx]
                    confidence = float(res[prediction_idx])
            
            # High-Performance UI Overlays
            # Top banner
            cv2.rectangle(image, (0,0), (640, 50), (28, 28, 28), -1) 
            text_str = f"Sign: {current_action.upper()} | Conf: {confidence*100:.1f}%"
            cv2.putText(image, text_str, (10,35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
            cv2.imshow('Sign Language AI Inference Core', image)
            
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    on_screen_prediction()
