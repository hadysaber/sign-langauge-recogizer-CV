"""
Defines the machine learning architecture.
"""

import sys
from pathlib import Path
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ACTIONS, SEQUENCE_LENGTH, NUM_FEATURES

def create_lstm_model() -> Model:
    """
    Constructs a lightweight sequential LSTM for fast edge inference.
    
    Returns:
        Model: The compiled Keras sequential model ready for fit/predict.
    """
    model = Sequential()
    
    # Input block: sequences of shape (SEQUENCE_LENGTH, NUM_FEATURES)
    model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)))
    model.add(LSTM(128, return_sequences=True, activation='relu'))
    model.add(LSTM(64, return_sequences=False, activation='relu'))
    
    # Dense classification block
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(len(ACTIONS), activation='softmax')) # Output layer matches number of classes
    
    # Compile with generic but highly robust Adam optimiser
    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    
    return model
