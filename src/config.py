import os

# Project Path Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
EXTRACTED_DATA_DIR = os.path.join(DATA_DIR, "extracted")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "sign_model.keras")

# Ensure required directories exist
for path in [RAW_DATA_DIR, EXTRACTED_DATA_DIR, MODEL_DIR]:
    os.makedirs(path, exist_ok=True)

# Application Parameters
# Use a default 3 actions for proof of concept. You can expand this to 20-50.
ACTIONS = ['hello', 'thanks', 'iloveyou']

# Video / Sequence configuration
SEQUENCE_LENGTH = 30  # 30 frames of sequence buffer
NO_SEQUENCES = 30     # How many videos to collect per action for training

# Feature dimension configuration
# Pose: 33 landmarks * 4 (x,y,z,visibility) = 132
# Face: omitted to keep it lightweight! (normally 468 * 3)
# Left hand: 21 * 3 = 63
# Right hand: 21 * 3 = 63
# Total features per frame = 132 + 63 + 63 = 258
NUM_FEATURES = 258 
