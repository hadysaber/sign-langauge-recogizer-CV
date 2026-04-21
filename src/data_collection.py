import cv2
import numpy as np
import os
import sys

# Ensure this accesses the root module correctly when run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import ACTIONS, NO_SEQUENCES, SEQUENCE_LENGTH, EXTRACTED_DATA_DIR
from src.extract import mp_holistic, mediapipe_detection, draw_styled_landmarks, extract_keypoints

def capture_data():
    """Loops through all specified actions, capturing sequences of frames for each gesture via webcam,
       extracts the landmarks, and saves them locally as .npy files.
    """
    # 1. Setup folders
    for action in ACTIONS:
        for sequence in range(NO_SEQUENCES):
            try: 
                os.makedirs(os.path.join(EXTRACTED_DATA_DIR, action, str(sequence)))
            except:
                pass

    # 2. Camera setup
    cap = cv2.VideoCapture(0)
    
    # 3. MediaPipe Holistic Model setup
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        for action in ACTIONS:
            for sequence in range(NO_SEQUENCES):
                for frame_num in range(SEQUENCE_LENGTH):
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to capture screen.")
                        break

                    # Detection and extraction
                    image, results = mediapipe_detection(frame, holistic)
                    draw_styled_landmarks(image, results)
                    
                    # UI feedback
                    if frame_num == 0: 
                        cv2.putText(image, 'STARTING COLLECTION', (120,200), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
                        cv2.putText(image, f'Collecting frames for {action} - Video {sequence}', (15,12), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.imshow('OpenCV Dataset Collection Feed', image)
                        cv2.waitKey(2000) # Give user a 2-second buffer to get ready
                    else: 
                        cv2.putText(image, f'Collecting frames for {action} - Video {sequence}', (15,12), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.imshow('OpenCV Dataset Collection Feed', image)
                    
                    # Export keypoints to Data Directory
                    keypoints = extract_keypoints(results)
                    npy_path = os.path.join(EXTRACTED_DATA_DIR, action, str(sequence), str(frame_num))
                    np.save(npy_path, keypoints)

                    # Elegant exit condition
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        print("Collection interrupted.")
                        cap.release()
                        cv2.destroyAllWindows()
                        return
                    
    cap.release()
    cv2.destroyAllWindows()
    print("Data collection completed successfully!")

if __name__ == '__main__':
    capture_data()
