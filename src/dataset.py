"""
Data loader and preprocessor for LSTM inputs.
"""

import numpy as np
import sys
import logging
from typing import Tuple
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ACTIONS, NO_SEQUENCES, SEQUENCE_LENGTH, EXTRACTED_DATA_DIR, NUM_FEATURES
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Loads all normalized keypoints from EXTRACTED_DATA_DIR and formats them into TimeSeries sequences.
    
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
        Train data (X), test data (X_test), train labels (y), test labels (y_test).
    """
    label_map = {label: num for num, label in enumerate(ACTIONS)}
    
    sequences, labels = [], []
    for action in ACTIONS:
        for sequence in range(NO_SEQUENCES):
            window = []
            for frame_num in range(SEQUENCE_LENGTH):
                file_path = EXTRACTED_DATA_DIR / action / str(sequence) / f"{frame_num}.npy"
                if file_path.exists():
                    res = np.load(str(file_path))
                    window.append(res)
                else: 
                    # Fallback to empty context if missing frames occur
                    logging.debug(f"Missing frame at {file_path}, padding with zeros.")
                    window.append(np.zeros(NUM_FEATURES))
            
            sequences.append(window)
            labels.append(label_map[action])
            
    X = np.array(sequences)
    y = to_categorical(labels).astype(int)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
    return X_train, X_test, y_train, y_test
