from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import ACTIONS, SEQUENCE_LENGTH, NUM_FEATURES

def create_lstm_model():
    """Constructs a lightweight sequential LSTM for fast edge inference."""
    model = Sequential()
    
    # Input block: sequences of shape (30, 258)
    model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)))
    model.add(LSTM(128, return_sequences=True, activation='relu'))
    model.add(LSTM(64, return_sequences=False, activation='relu'))
    
    # Dense classification block
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(len(ACTIONS), activation='softmax')) # Softmax distribution for N classes
    
    # Compile with generic but highly robust Adam optimiser
    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    
    return model
