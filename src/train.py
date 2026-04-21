"""
Training orchestrator script.
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    import tensorflow as tf
    from tensorflow.keras.callbacks import TensorBoard, EarlyStopping
except ImportError as e:
    logging.error(f"Missing critical dependency: {e.name}. Please ensure you run 'pip install -r requirements.txt'")
    sys.exit(1)

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.dataset import load_data
from src.model import create_lstm_model
from src.config import MODEL_PATH

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def train() -> None:
    """
    Executes the training loop end-to-end and saves the optimized weights.
    """
    logging.info("Loading Dataset Sequence...")
    X_train, X_test, y_train, y_test = load_data()
    
    log_dir = MODEL_PATH.parent / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup callbacks
    tb_callback = TensorBoard(log_dir=str(log_dir))
    early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    
    logging.info("Initializing LSTM Vector Engine...")
    model = create_lstm_model()
    
    logging.info("Starting Training Cycle. This will utilize available accelerator compute automatically.")
    model.fit(X_train, y_train, 
              validation_data=(X_test, y_test), 
              epochs=250, 
              callbacks=[tb_callback, early_stop])
    
    logging.info(f"Saving optimal weights to {MODEL_PATH} ...")
    model.save(str(MODEL_PATH))
    logging.info("Training Run Complete!")

if __name__ == '__main__':
    train()
