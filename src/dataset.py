import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import ACTIONS, NO_SEQUENCES, SEQUENCE_LENGTH, EXTRACTED_DATA_DIR, NUM_FEATURES
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

def load_data():
    """Loads all normalized keypoints from EXTRACTED_DATA_DIR and formats them into TimeSeries sequences."""
    label_map = {label:num for num, label in enumerate(ACTIONS)}
    
    sequences, labels = [], []
    for action in ACTIONS:
        for sequence in range(NO_SEQUENCES):
            window = []
            for frame_num in range(SEQUENCE_LENGTH):
                try:
                    res = np.load(os.path.join(EXTRACTED_DATA_DIR, action, str(sequence), f"{frame_num}.npy"))
                    window.append(res)
                except FileNotFoundError:
                    # Simple padding fallback
                    window.append(np.zeros(NUM_FEATURES))
            
            sequences.append(window)
            labels.append(label_map[action])
            
    X = np.array(sequences)
    y = to_categorical(labels).astype(int)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
    return X_train, X_test, y_train, y_test
