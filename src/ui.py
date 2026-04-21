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
    """
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
        )
        
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
        )
        
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4), 
            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
        )

def draw_collection_header(image: np.ndarray, action: str, sequence: int, is_starting: bool = False) -> None:
    """
    Draws the header banner for the data collection script.
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

def draw_presentation_overlay(
    image: np.ndarray, 
    status_text: str, 
    action: str, 
    confidence: float, 
    fps: int,
    smoothing_active: bool
) -> None:
    """
    Renders a comprehensive, graduation-ready demo UI over the frame.
    
    Args:
        image (np.ndarray): Target image canvas.
        status_text (str): Top level state e.g., 'Waiting for sequence...', 'No hands detected'.
        action (str): The current predicted sign language action.
        confidence (float): Probability score.
        fps (int): Frame rate integer.
        smoothing_active (bool): Indicator if consensus logic is active.
    """
    # Base styling rectangles
    cv2.rectangle(image, (0, 0), (640, 80), (35, 35, 35), -1) 
    
    # 1. Determine Status Color (Red for warning, yellow for wait, green for active)
    status_color = (0, 255, 0)
    if "No hands" in status_text:
        status_color = (50, 50, 255) # Light Red
    elif "Waiting" in status_text:
        status_color = (0, 200, 255) # Yellow
        
    # Draw Status
    cv2.putText(image, f"Status: {status_text}", (10, 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2, cv2.LINE_AA)
                
    # 2. Draw Prediction and Confidence if we are active
    if "Predicting" in status_text and action and action != "Waiting...":
        text_str = f"Sign: {action.upper()}  |  Conf: {confidence * 100:.1f}%"
        cv2.putText(image, text_str, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(image, "Sign: ---", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (150, 150, 150), 2, cv2.LINE_AA)
        
    # 3. Draw Engine Metrics (FPS and Smoothing)
    cv2.putText(image, f"FPS: {fps}", (520, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    smooth_color = (0, 255, 0) if smoothing_active else (100, 100, 100)
    cv2.putText(image, f"SMOOTH: {'ON' if smoothing_active else 'OFF'}", (520, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, smooth_color, 1, cv2.LINE_AA)
    
    # 4. Draw Command Help Footer
    h, w, _ = image.shape
    help_str = "Press: [q] Quit  |  [r] Reset Buffer  |  [s] Toggle Smoothing"
    cv2.rectangle(image, (0, h-30), (w, h), (20, 20, 20), -1)
    cv2.putText(image, help_str, (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)

