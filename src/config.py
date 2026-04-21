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
ACTIONS: List[str] = ['hello', 'thanks', 'iloveyou']
CONFIDENCE_THRESHOLD: float = 0.70

# ──────────────────────────────────────────────
# Training Hyperparameters (edit these for experiments)
# ──────────────────────────────────────────────
EPOCHS: int = 250
BATCH_SIZE: int = 16
LEARNING_RATE: float = 0.001
TEST_SIZE: float = 0.10        # fraction held out for validation / evaluation
ES_PATIENCE: int = 15          # early-stopping patience (epochs)

# ──────────────────────────────────────────────
# Video / Sequence Configuration
# ──────────────────────────────────────────────
SEQUENCE_LENGTH: int = 30      # 30 frames of sequence buffer
NO_SEQUENCES: int = 30         # how many videos to collect per action

# ──────────────────────────────────────────────
# Feature Extraction Dimensions
# ──────────────────────────────────────────────
POSE_LANDMARKS: int = 33
HAND_LANDMARKS: int = 21

POSE_DIM: int = POSE_LANDMARKS * 4  # (x, y, z, visibility)
HAND_DIM: int = HAND_LANDMARKS * 3  # (x, y, z)

# Total features per frame = 132 + 63 + 63 = 258
NUM_FEATURES: int = POSE_DIM + (HAND_DIM * 2)
