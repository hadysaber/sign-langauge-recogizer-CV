"""
Module for encapsulating all OpenCV rendering and graphical UI elements.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Any

from src.config import ACTIONS

# Initialize references
mp_holistic: Any = mp.solutions.holistic
mp_drawing: Any = mp.solutions.drawing_utils

def draw_styled_landmarks(image: np.ndarray, results: Any) -> None:
    """
    Draws holistic landmarks with custom styling directly onto the image.
    
    Args:
        image (np.ndarray): The OpenCV frame.
        results (Any): The MediaPipe results.
    """
    # Draw pose connections
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
        )
        
    # Draw left hand connections
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
        )
        
    # Draw right hand connections
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
        )

def draw_collection_header(image: np.ndarray, action: str, sequence: int, is_starting: bool = False) -> None:
    """
    Draws the header banner for the data collection script.
    
    Args:
        image (np.ndarray): The OpenCV frame.
        action (str): The current action being tracked.
        sequence (int): The current sequence number.
        is_starting (bool): Flag indicating if the sequence is just beginning (will wait).
    """
    if is_starting:
        cv2.putText(
            image, 'STARTING COLLECTION', (120, 200), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4, cv2.LINE_AA
        )
        
    cv2.putText(
        image, f'Collecting frames for {action} - Video {sequence}', (15, 25), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA
    )

def draw_inference_overlay(image: np.ndarray, action: str, confidence: float) -> None:
    """
    Draws the real-time inference prediction bar at the top of the frame.
    
    Args:
        image (np.ndarray): The OpenCV frame.
        action (str): The predicted action string.
        confidence (float): Probability score (0.0 to 1.0).
    """
    # Base dark banner
    cv2.rectangle(image, (0, 0), (640, 50), (28, 28, 28), -1) 
    
    # Output rendering
    text_str = f"Sign: {action.upper()} | Conf: {confidence * 100:.1f}%"
    cv2.putText(
        image, text_str, (10, 35), 
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
    )
