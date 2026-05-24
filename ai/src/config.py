"""
Configuration module for the Sign Language Recognition system.
Defines paths, model hyperparameters, training settings, and UI constants.
"""

from pathlib import Path
from typing import List

# ──────────────────────────────────────────────
# Project Path Setup
# ──────────────────────────────────────────────
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
EXTRACTED_DATA_DIR: Path = DATA_DIR / "extracted"

# Model output paths
MODEL_DIR: Path = PROJECT_ROOT / "models"
MODEL_PATH: Path = MODEL_DIR / "sign_model.keras"
BEST_MODEL_PATH: Path = MODEL_DIR / "sign_model_best.keras"
LABEL_MAP_PATH: Path = MODEL_DIR / "label_mapping.json"
MODEL_METADATA_PATH: Path = MODEL_DIR / "model_metadata.json"
LOG_DIR: Path = MODEL_DIR / "Logs"

# Report output paths
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
PLOTS_DIR: Path = REPORTS_DIR / "plots"
METRICS_DIR: Path = REPORTS_DIR / "metrics"
HISTORY_PATH: Path = REPORTS_DIR / "training_history.json"

# Ensure all required directories exist at import time
for _path in [RAW_DATA_DIR, EXTRACTED_DATA_DIR, MODEL_DIR, LOG_DIR,
              REPORTS_DIR, PLOTS_DIR, METRICS_DIR]:
    _path.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Application / Inference Parameters
# ──────────────────────────────────────────────
ACTIONS: List[str] = [
    'hello', 'thanks', 'iloveyou',
    'my_name_is', 'hady', 'i_am_from', 'egypt'
]
CONFIDENCE_THRESHOLD: float = 0.70
RANDOM_SEED: int = 42

# ──────────────────────────────────────────────
# Training Hyperparameters (edit these for experiments)
# ──────────────────────────────────────────────
EPOCHS: int = 250
BATCH_SIZE: int = 16
LEARNING_RATE: float = 0.001
VALIDATION_SIZE: float = 0.15  # fraction used for early stopping / checkpointing
TEST_SIZE: float = 0.15        # final untouched evaluation fraction
ES_PATIENCE: int = 15          # early-stopping patience (epochs)
LR_PATIENCE: int = 6           # reduce learning rate after stagnant validation loss

# ──────────────────────────────────────────────
# Video / Sequence Configuration
# ──────────────────────────────────────────────
SEQUENCE_LENGTH: int = 30      # 30 frames of sequence buffer
NO_SEQUENCES: int = 60         # videos per action (60+ recommended for better accuracy)
MAX_MISSING_RATIO: float = 0.20
MIN_HAND_FRAMES_RATIO: float = 0.70

# ──────────────────────────────────────────────
# Feature Extraction Dimensions
# ──────────────────────────────────────────────
POSE_LANDMARKS: int = 33
HAND_LANDMARKS: int = 21

POSE_DIM: int = POSE_LANDMARKS * 4  # (x, y, z, visibility)
HAND_DIM: int = HAND_LANDMARKS * 3  # (x, y, z)

# Total features per frame = 132 + 63 + 63 = 258
NUM_FEATURES: int = POSE_DIM + (HAND_DIM * 2)

# ──────────────────────────────────────────────
# Accuracy / Robustness Options
# ──────────────────────────────────────────────
NORMALIZE_LANDMARKS: bool = True
AUGMENT_TRAINING_DATA: bool = True
AUGMENTATION_COPIES: int = 2
AUGMENT_NOISE_STD: float = 0.01
AUGMENT_SCALE_RANGE: tuple[float, float] = (0.95, 1.05)
AUGMENT_TIME_SHIFT: int = 2
