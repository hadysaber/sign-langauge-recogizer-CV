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
    EXTRACTED_DATA_DIR, NUM_FEATURES, TEST_SIZE, VALIDATION_SIZE,
    LABEL_MAP_PATH, POSE_DIM, HAND_DIM, MAX_MISSING_RATIO,
    MIN_HAND_FRAMES_RATIO, NORMALIZE_LANDMARKS, AUGMENT_TRAINING_DATA,
    AUGMENTATION_COPIES, AUGMENT_NOISE_STD, AUGMENT_SCALE_RANGE,
    AUGMENT_TIME_SHIFT, RANDOM_SEED
)
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

logger = logging.getLogger(__name__)

EPSILON = 1e-6


def _coordinate_feature_mask() -> np.ndarray:
    """Returns a mask for x/y/z features, excluding pose visibility."""
    mask = np.ones(NUM_FEATURES, dtype=bool)
    pose_visibility_indices = np.arange(3, POSE_DIM, 4)
    mask[pose_visibility_indices] = False
    return mask


COORDINATE_FEATURE_MASK = _coordinate_feature_mask()


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


def _has_hand_landmarks(frame: np.ndarray) -> bool:
    """Checks whether either hand section contains detected landmarks."""
    hands = frame[POSE_DIM:POSE_DIM + (HAND_DIM * 2)]
    return not np.allclose(hands, 0.0)


def normalize_sequence(sequence: np.ndarray) -> np.ndarray:
    """
    Normalizes each frame around the signer instead of the camera frame.

    MediaPipe x/y coordinates are image-relative, so the same gesture can look
    different if the signer moves closer, farther, left, or right. This keeps
    missing landmarks at zero and preserves pose visibility values.
    """
    normalized = sequence.astype(np.float32, copy=True)

    for frame_idx in range(normalized.shape[0]):
        frame = normalized[frame_idx]
        pose = frame[:POSE_DIM].reshape(-1, 4)
        left_hand = frame[POSE_DIM:POSE_DIM + HAND_DIM].reshape(-1, 3)
        right_hand = frame[POSE_DIM + HAND_DIM:].reshape(-1, 3)

        pose_mask = np.any(np.abs(pose[:, :3]) > EPSILON, axis=1)
        left_mask = np.any(np.abs(left_hand) > EPSILON, axis=1)
        right_mask = np.any(np.abs(right_hand) > EPSILON, axis=1)

        present_points = []
        if np.any(pose_mask):
            present_points.append(pose[pose_mask, :3])
        if np.any(left_mask):
            present_points.append(left_hand[left_mask])
        if np.any(right_mask):
            present_points.append(right_hand[right_mask])

        if not present_points:
            continue

        all_points = np.vstack(present_points)

        # Prefer shoulder width as the scale anchor when both shoulders exist.
        if pose_mask.size > 12 and pose_mask[11] and pose_mask[12]:
            center = (pose[11, :3] + pose[12, :3]) / 2.0
            scale = float(np.linalg.norm(pose[11, :2] - pose[12, :2]))
        else:
            center = np.mean(all_points, axis=0)
            xy_range = np.ptp(all_points[:, :2], axis=0)
            scale = float(max(np.max(xy_range), EPSILON))

        scale = max(scale, 0.05)

        pose[pose_mask, :3] = (pose[pose_mask, :3] - center) / scale
        left_hand[left_mask] = (left_hand[left_mask] - center) / scale
        right_hand[right_mask] = (right_hand[right_mask] - center) / scale

    return normalized


def _augment_sequence(sequence: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Applies light train-only augmentation to reduce overfitting."""
    augmented = sequence.astype(np.float32, copy=True)

    if AUGMENT_TIME_SHIFT > 0:
        shift = int(rng.integers(-AUGMENT_TIME_SHIFT, AUGMENT_TIME_SHIFT + 1))
        if shift > 0:
            augmented[shift:] = augmented[:-shift]
            augmented[:shift] = 0.0
        elif shift < 0:
            augmented[:shift] = augmented[-shift:]
            augmented[shift:] = 0.0

    scale = float(rng.uniform(AUGMENT_SCALE_RANGE[0], AUGMENT_SCALE_RANGE[1]))
    active_coords = COORDINATE_FEATURE_MASK & (np.abs(augmented) > EPSILON)
    augmented[active_coords] *= scale

    noise = rng.normal(0.0, AUGMENT_NOISE_STD, size=augmented.shape).astype(np.float32)
    augmented[active_coords] += noise[active_coords]

    return augmented


def augment_training_data(
    X_train: np.ndarray,
    y_train: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Expands only the training split, keeping validation/test honest."""
    if not AUGMENT_TRAINING_DATA or AUGMENTATION_COPIES <= 0:
        return X_train, y_train

    rng = np.random.default_rng(RANDOM_SEED)
    augmented_X = [X_train]
    augmented_y = [y_train]

    for _ in range(AUGMENTATION_COPIES):
        augmented_X.append(np.array([
            _augment_sequence(sequence, rng) for sequence in X_train
        ], dtype=np.float32))
        augmented_y.append(y_train.copy())

    X_out = np.concatenate(augmented_X, axis=0)
    y_out = np.concatenate(augmented_y, axis=0)
    logger.info(
        f"Training augmentation: {X_train.shape[0]} -> {X_out.shape[0]} samples "
        f"({AUGMENTATION_COPIES} synthetic copies)"
    )
    return X_out, y_out


def load_data(
    augment_train: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Loads keypoint sequences from EXTRACTED_DATA_DIR, validates each
    sequence for completeness, and formats them for LSTM training.

    Sequences with too many missing frames (> MAX_MISSING_RATIO) are
    skipped and logged. Remaining sequences with minor gaps are
    zero-padded.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        X_train, X_val, X_test, y_train, y_val, y_test
    """
    label_map = get_label_map()
    max_missing = int(SEQUENCE_LENGTH * MAX_MISSING_RATIO)
    min_hand_frames = int(np.ceil(SEQUENCE_LENGTH * MIN_HAND_FRAMES_RATIO))

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
            hand_frames = 0

            for frame_num in range(SEQUENCE_LENGTH):
                file_path = seq_dir / f"{frame_num}.npy"
                if file_path.exists():
                    res = np.load(str(file_path)).astype(np.float32)
                    if res.shape[0] != NUM_FEATURES:
                        logger.warning(
                            f"{action}/seq{seq_idx}/frame{frame_num}: "
                            f"expected {NUM_FEATURES} features, got {res.shape[0]}"
                        )
                        missing_count += 1
                        res = np.zeros(NUM_FEATURES, dtype=np.float32)
                    if _has_hand_landmarks(res):
                        hand_frames += 1
                    window.append(res)
                else:
                    missing_count += 1
                    window.append(np.zeros(NUM_FEATURES, dtype=np.float32))

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
            elif hand_frames < min_hand_frames:
                skipped += 1
                action_skipped += 1
                skipped_details.append(
                    f"  {action}/seq{seq_idx}: only {hand_frames}/"
                    f"{SEQUENCE_LENGTH} frames contain hand landmarks"
                )
            else:
                sequence_array = np.array(window, dtype=np.float32)
                if NORMALIZE_LANDMARKS:
                    sequence_array = normalize_sequence(sequence_array)
                sequences.append(sequence_array)
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

    X = np.array(sequences, dtype=np.float32)
    labels_array = np.array(labels, dtype=np.int32)
    y = to_categorical(labels_array, num_classes=len(ACTIONS)).astype(np.float32)

    logger.info(f"Dataset shape: {X.shape[0]} sequences × "
                f"{X.shape[1]} frames × {X.shape[2]} features")
    logger.info(f"Classes ({len(ACTIONS)}): {ACTIONS}")

    class_counts = np.bincount(labels_array, minlength=len(ACTIONS))
    logger.info(f"Class distribution: {dict(zip(ACTIONS, class_counts))}")

    holdout_size = VALIDATION_SIZE + TEST_SIZE
    if holdout_size <= 0 or holdout_size >= 0.8:
        logger.error("VALIDATION_SIZE + TEST_SIZE must be between 0 and 0.8")
        sys.exit(1)

    # Train/validation/test split. The test set remains untouched by training.
    X_train, X_holdout, y_train, y_holdout, labels_train, labels_holdout = train_test_split(
        X, y, labels_array,
        test_size=holdout_size,
        random_state=RANDOM_SEED,
        stratify=labels_array
    )

    relative_test_size = TEST_SIZE / holdout_size
    X_val, X_test, y_val, y_test, labels_val, labels_test = train_test_split(
        X_holdout, y_holdout, labels_holdout,
        test_size=relative_test_size,
        random_state=RANDOM_SEED,
        stratify=labels_holdout
    )

    if augment_train:
        X_train, y_train = augment_training_data(X_train, y_train)

    logger.info(
        f"Train: {X_train.shape[0]} | Validation: {X_val.shape[0]} | "
        f"Test: {X_test.shape[0]} "
        f"(val={VALIDATION_SIZE}, test={TEST_SIZE})"
    )
    logger.info(
        f"Validation distribution: "
        f"{dict(zip(ACTIONS, np.bincount(labels_val, minlength=len(ACTIONS))))}"
    )
    logger.info(
        f"Test distribution: "
        f"{dict(zip(ACTIONS, np.bincount(labels_test, minlength=len(ACTIONS))))}"
    )

    return X_train, X_val, X_test, y_train, y_val, y_test
