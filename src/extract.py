"""
Module for extracting MediaPipe landmarks from images.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Any

from src.config import POSE_DIM, HAND_DIM

# MediaPipe Solutions
mp_holistic: Any = mp.solutions.holistic

def mediapipe_detection(image: np.ndarray, model: Any) -> Tuple[np.ndarray, Any]:
    """
    Processes the image and extracts landmarks using the provided model.
    
    Args:
        image (np.ndarray): The OpenCV BGR image frame.
        model (Any): The instantiated MediaPipe holistic model.
        
    Returns:
        Tuple[np.ndarray, Any]: The processed image and the prediction results.
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Color conversion BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # Color conversion RGB 2 BGR
    return image, results


def extract_keypoints(results: Any) -> np.ndarray:
    """
    Flattens the pose, left hand, and right hand landmarks into a single 1D numpy array.
    
    Args:
        results (Any): MediaPipe detection results.
        
    Returns:
        np.ndarray: A flattened sequence of coordinates padded dynamically.
    """
    # Extract Hand and Pose coordinates if available, else pad with zero vectors.
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(POSE_DIM)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(HAND_DIM)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(HAND_DIM)
    
    return np.concatenate([pose, lh, rh])
