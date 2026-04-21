"""
Defines the machine learning architecture.
"""

import sys
from pathlib import Path
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ACTIONS, SEQUENCE_LENGTH, NUM_FEATURES

def create_lstm_model(learning_rate: float = 0.001) -> Model:
    """
    Constructs a lightweight sequential LSTM for fast edge inference.
    
    Args:
        learning_rate (float): Learning rate for the Adam optimizer.
                               Defaults to 0.001 for backward compatibility.
    
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
    
    # Compile with Adam optimizer at the specified learning rate
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['categorical_accuracy']
    )
    
    return model

