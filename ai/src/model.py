"""
Defines the machine learning architecture.
"""

import sys
from pathlib import Path
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ACTIONS, SEQUENCE_LENGTH, NUM_FEATURES

def create_lstm_model(learning_rate: float = 0.001) -> Model:
    """
    Constructs a lightweight sequential LSTM sized for small-dataset
    training (tens to low-hundreds of samples per class).

    Architecture notes:
      - Uses default tanh activation for LSTMs (stable gradients).
        ReLU in LSTMs causes exploding gradients on small datasets.
      - Dropout between layers to reduce overfitting.
      - Smaller layer widths to match typical dataset sizes.

    Args:
        learning_rate (float): Learning rate for the Adam optimizer.
                               Defaults to 0.001 for backward compatibility.

    Returns:
        Model: The compiled Keras sequential model ready for fit/predict.
    """
    model = Sequential()

    # Input block: sequences of shape (SEQUENCE_LENGTH, NUM_FEATURES)
    # Using default tanh activation (NOT relu — relu causes gradient explosions in LSTMs)
    model.add(LSTM(64, return_sequences=True, input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)))
    model.add(Dropout(0.3))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.3))

    # Dense classification block
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(len(ACTIONS), activation='softmax'))

    # Compile with Adam optimizer at the specified learning rate
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['categorical_accuracy']
    )

    return model
