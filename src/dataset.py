"""
Data loader and preprocessor for LSTM inputs.
"""

import json
import numpy as np
import sys
import logging
from typing import Tuple, Dict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import (
    ACTIONS, NO_SEQUENCES, SEQUENCE_LENGTH,
    EXTRACTED_DATA_DIR, NUM_FEATURES, TEST_SIZE, LABEL_MAP_PATH
)
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

logger = logging.getLogger(__name__)


def get_label_map() -> Dict[str, int]:
    """Returns the label-to-index mapping derived from ACTIONS."""
    return {label: idx for idx, label in enumerate(ACTIONS)}


def save_label_mapping() -> Path:
    """
    Persists the label mapping to a JSON file so inference stays aligned
    with the trained model, even if ACTIONS order changes later.

    Returns:
        Path: The path the mapping was saved to.
    """
    label_map = get_label_map()
    with open(LABEL_MAP_PATH, 'w') as f:
        json.dump(label_map, f, indent=2)
    logger.info(f"Label mapping saved → {LABEL_MAP_PATH}")
    return LABEL_MAP_PATH


def load_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Loads all normalized keypoints from EXTRACTED_DATA_DIR and formats
    them into TimeSeries sequences suitable for LSTM training.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        X_train, X_test, y_train, y_test
    """
    label_map = get_label_map()

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

    # Informative logging
    logger.info(f"Dataset loaded: {X.shape[0]} sequences, "
                f"{X.shape[1]} frames × {X.shape[2]} features")
    logger.info(f"Classes ({len(ACTIONS)}): {ACTIONS}")
    logger.info(f"Label distribution: {dict(zip(ACTIONS, np.bincount(labels)))}")

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=42, stratify=labels
    )
    logger.info(f"Train size: {X_train.shape[0]} | Test size: {X_test.shape[0]} "
                f"(split={TEST_SIZE})")

    return X_train, X_test, y_train, y_test
