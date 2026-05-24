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

# A sequence with more than this fraction of missing frames is skipped
MAX_MISSING_RATIO = 0.25  # e.g., at most 7 of 30 frames can be missing


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
    Loads keypoint sequences from EXTRACTED_DATA_DIR, validates each
    sequence for completeness, and formats them for LSTM training.

    Sequences with too many missing frames (> MAX_MISSING_RATIO) are
    skipped and logged. Remaining sequences with minor gaps are
    zero-padded.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        X_train, X_test, y_train, y_test
    """
    label_map = get_label_map()
    max_missing = int(SEQUENCE_LENGTH * MAX_MISSING_RATIO)

    sequences, labels = [], []
    total_scanned = 0
    skipped = 0
    skipped_details = []

    for action in ACTIONS:
        action_valid = 0
        action_skipped = 0

        for seq_idx in range(NO_SEQUENCES):
            seq_dir = EXTRACTED_DATA_DIR / action / str(seq_idx)
            window = []
            missing_count = 0

            for frame_num in range(SEQUENCE_LENGTH):
                file_path = seq_dir / f"{frame_num}.npy"
                if file_path.exists():
                    res = np.load(str(file_path))
                    window.append(res)
                else:
                    missing_count += 1
                    window.append(np.zeros(NUM_FEATURES))

            total_scanned += 1

            if missing_count > max_missing:
                # Sequence is too damaged to be useful
                skipped += 1
                action_skipped += 1
                if missing_count == SEQUENCE_LENGTH:
                    reason = "completely empty"
                else:
                    reason = f"{missing_count}/{SEQUENCE_LENGTH} frames missing"
                skipped_details.append(f"  {action}/seq{seq_idx}: {reason}")
            else:
                sequences.append(window)
                labels.append(label_map[action])
                action_valid += 1
                if missing_count > 0:
                    logger.debug(
                        f"{action}/seq{seq_idx}: {missing_count} frames "
                        f"missing (padded with zeros)"
                    )

        logger.info(f"  {action}: {action_valid} valid, "
                    f"{action_skipped} skipped")

    # ── Summary ──
    logger.info(f"Scanned {total_scanned} sequences total")
    logger.info(f"  Valid:   {len(sequences)}")
    logger.info(f"  Skipped: {skipped} (>{int(MAX_MISSING_RATIO*100)}% frames missing)")

    if skipped_details:
        logger.warning("Skipped sequences:")
        for detail in skipped_details:
            logger.warning(detail)

    if len(sequences) == 0:
        logger.error(
            "No valid sequences found! Collect data first with "
            "'python src/data_collection.py'"
        )
        sys.exit(1)

    # Check for class imbalance
    unique_labels = set(labels)
    if len(unique_labels) < len(ACTIONS):
        missing_classes = [a for a in ACTIONS if label_map[a] not in unique_labels]
        logger.error(
            f"Missing data for classes: {missing_classes}. "
            f"Collect data for ALL classes before training."
        )
        sys.exit(1)

    X = np.array(sequences)
    y = to_categorical(labels, num_classes=len(ACTIONS)).astype(int)

    logger.info(f"Dataset shape: {X.shape[0]} sequences × "
                f"{X.shape[1]} frames × {X.shape[2]} features")
    logger.info(f"Classes ({len(ACTIONS)}): {ACTIONS}")

    class_counts = np.bincount(labels, minlength=len(ACTIONS))
    logger.info(f"Class distribution: {dict(zip(ACTIONS, class_counts))}")

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=42, stratify=labels
    )
    logger.info(f"Train: {X_train.shape[0]} | Test: {X_test.shape[0]} "
                f"(split={TEST_SIZE})")

    return X_train, X_test, y_train, y_test
