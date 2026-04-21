"""
Configuration module for the Sign Language Recognition system.
Defines paths, model hyperparameters, and UI constants.
"""

from pathlib import Path
from typing import List

# Project Path Setup
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
EXTRACTED_DATA_DIR: Path = DATA_DIR / "extracted"
MODEL_DIR: Path = PROJECT_ROOT / "models"
MODEL_PATH: Path = MODEL_DIR / "sign_model.keras"

# Ensure required directories exist
for path in [RAW_DATA_DIR, EXTRACTED_DATA_DIR, MODEL_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Application Parameters
ACTIONS: List[str] = ['hello', 'thanks', 'iloveyou']
CONFIDENCE_THRESHOLD: float = 0.70

# Video / Sequence configuration
SEQUENCE_LENGTH: int = 30  # 30 frames of sequence buffer
NO_SEQUENCES: int = 30     # How many videos to collect per action for training

# Feature Extraction Dimensions
POSE_LANDMARKS: int = 33
HAND_LANDMARKS: int = 21

POSE_DIM: int = POSE_LANDMARKS * 4  # (x, y, z, visibility)
HAND_DIM: int = HAND_LANDMARKS * 3  # (x, y, z)

# Total features per frame = 132 + 63 + 63 = 258
NUM_FEATURES: int = POSE_DIM + (HAND_DIM * 2)
