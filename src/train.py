import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tensorflow.keras.callbacks import TensorBoard, EarlyStopping
from src.dataset import load_data
from src.model import create_lstm_model
from src.config import MODEL_PATH

def train():
    """Executes the training loop end-to-end and saves the optimized weights."""
    print("-> Loading Dataset Sequence...")
    X_train, X_test, y_train, y_test = load_data()
    
    log_dir = os.path.join(os.path.dirname(MODEL_PATH), 'Logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Setup callbacks
    tb_callback = TensorBoard(log_dir=log_dir)
    early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    
    print("-> Initializing LSTM Vector Engine...")
    model = create_lstm_model()
    
    print("-> Starting Training Cycle...")
    model.fit(X_train, y_train, 
              validation_data=(X_test, y_test), 
              epochs=250, 
              callbacks=[tb_callback, early_stop])
    
    print(f"-> Saving optimal weights to {MODEL_PATH} ...")
    model.save(MODEL_PATH)
    print("-> Complete!")

if __name__ == '__main__':
    train()
