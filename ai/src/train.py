"""
Training orchestrator for the Sign Language Recognition LSTM model.

Handles end-to-end training, saves the best and final models, persists
training history, generates accuracy/loss plots, and exports the label
mapping used during training.

Usage:
    python src/train.py
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend (no GUI needed)
    import matplotlib.pyplot as plt
    import tensorflow as tf
    from tensorflow.keras.callbacks import (
        TensorBoard, EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    )
except ImportError as e:
    logger.error(
        f"Missing critical dependency: {e.name}. "
        "Please run 'pip install -r requirements.txt'"
    )
    sys.exit(1)

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.dataset import load_data, save_label_mapping
from src.model import create_lstm_model
from src.config import (
    MODEL_PATH, BEST_MODEL_PATH, LOG_DIR, HISTORY_PATH,
    PLOTS_DIR, ACTIONS, LABEL_MAP_PATH, MODEL_METADATA_PATH,
    EPOCHS, BATCH_SIZE, LEARNING_RATE, ES_PATIENCE, LR_PATIENCE,
    VALIDATION_SIZE, TEST_SIZE, RANDOM_SEED, NORMALIZE_LANDMARKS,
    AUGMENT_TRAINING_DATA, AUGMENTATION_COPIES
)


# ──────────────────────────────────────────────
# Plot Helpers
# ──────────────────────────────────────────────

def _save_curve(history: dict, train_key: str, val_key: str,
                ylabel: str, title: str, filename: str) -> Path:
    """Generates and saves a single training curve plot."""
    out_path = PLOTS_DIR / filename
    plt.figure(figsize=(10, 6))
    plt.plot(history[train_key], label='Train', linewidth=2)
    plt.plot(history[val_key], label='Validation', linewidth=2)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_path), dpi=150)
    plt.close()
    logger.info(f"Plot saved → {out_path}")
    return out_path


def save_training_plots(history: dict) -> None:
    """Generates accuracy and loss plots from the training history."""
    _save_curve(
        history,
        train_key='categorical_accuracy',
        val_key='val_categorical_accuracy',
        ylabel='Accuracy',
        title='Training vs Validation Accuracy',
        filename='accuracy.png'
    )
    _save_curve(
        history,
        train_key='loss',
        val_key='val_loss',
        ylabel='Loss',
        title='Training vs Validation Loss',
        filename='loss.png'
    )


def save_training_history(history: dict) -> Path:
    """Persists the raw training history as JSON for later analysis."""
    # Convert numpy float32 values to plain Python floats for JSON
    serializable = {k: [float(v) for v in vals] for k, vals in history.items()}
    serializable['saved_at'] = datetime.now().isoformat()
    serializable['epochs_completed'] = len(history['loss'])

    with open(HISTORY_PATH, 'w') as f:
        json.dump(serializable, f, indent=2)
    logger.info(f"Training history saved → {HISTORY_PATH}")
    return HISTORY_PATH


def save_model_metadata(test_loss: float, test_acc: float) -> Path:
    """Saves training/preprocessing settings needed for reliable inference."""
    metadata = {
        "saved_at": datetime.now().isoformat(),
        "actions": ACTIONS,
        "normalize_landmarks": NORMALIZE_LANDMARKS,
        "augmentation_enabled": AUGMENT_TRAINING_DATA,
        "augmentation_copies": AUGMENTATION_COPIES,
        "validation_size": VALIDATION_SIZE,
        "test_size": TEST_SIZE,
        "holdout_test_loss": round(float(test_loss), 4),
        "holdout_test_accuracy": round(float(test_acc), 4),
    }
    with open(MODEL_METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Model metadata saved → {MODEL_METADATA_PATH}")
    return MODEL_METADATA_PATH


# ──────────────────────────────────────────────
# Main Training Function
# ──────────────────────────────────────────────

def train() -> None:
    """
    Executes the full training pipeline:
      1. Load & split dataset
      2. Save label mapping
      3. Build model with configured hyperparameters
      4. Train with checkpointing, early stopping, TensorBoard
      5. Save final model, training history, and plots
    """
    logger.info("=" * 60)
    logger.info("  Sign Language LSTM — Training Pipeline")
    logger.info("=" * 60)

    # ── 1. Configuration Summary ──
    logger.info(f"Hyperparameters:")
    logger.info(f"  Epochs:          {EPOCHS}")
    logger.info(f"  Batch size:      {BATCH_SIZE}")
    logger.info(f"  Learning rate:   {LEARNING_RATE}")
    logger.info(f"  Early stopping:  patience={ES_PATIENCE}")
    logger.info(f"  Split:           val={VALIDATION_SIZE}, test={TEST_SIZE}")
    logger.info(f"  Classes:         {ACTIONS}")
    tf.keras.utils.set_random_seed(RANDOM_SEED)

    # ── 2. Load Dataset ──
    logger.info("-" * 60)
    logger.info("Loading dataset...")
    X_train, X_val, X_test, y_train, y_val, y_test = load_data()

    # ── 3. Save Label Mapping ──
    save_label_mapping()

    # ── 4. Build Model ──
    logger.info("-" * 60)
    logger.info("Initializing LSTM model...")
    model = create_lstm_model(learning_rate=LEARNING_RATE)
    model.summary(print_fn=logger.info)

    # ── 5. Setup Callbacks ──
    callbacks = [
        ModelCheckpoint(
            filepath=str(BEST_MODEL_PATH),
            monitor='val_loss',
            save_best_only=True,
            mode='min',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=ES_PATIENCE,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=LR_PATIENCE,
            min_lr=1e-5,
            verbose=1
        ),
        TensorBoard(log_dir=str(LOG_DIR))
    ]

    # ── 6. Train ──
    logger.info("-" * 60)
    logger.info("Starting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )

    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)

    # ── 7. Save Final Model ──
    logger.info("-" * 60)
    model.save(str(MODEL_PATH))
    logger.info(f"Final model saved → {MODEL_PATH}")

    # ── 8. Save History & Plots ──
    save_training_history(history.history)
    save_training_plots(history.history)
    save_model_metadata(test_loss, test_acc)

    # ── 9. Done ──
    logger.info("=" * 60)
    best_val_acc = max(history.history['val_categorical_accuracy'])
    final_val_loss = history.history['val_loss'][-1]
    logger.info(f"Training complete!")
    logger.info(f"  Best val accuracy: {best_val_acc:.4f}")
    logger.info(f"  Holdout test acc:  {test_acc:.4f}")
    logger.info(f"  Holdout test loss: {test_loss:.4f}")
    logger.info(f"  Final val loss:    {final_val_loss:.4f}")
    logger.info(f"  Epochs completed:  {len(history.history['loss'])}")
    logger.info(f"Outputs:")
    logger.info(f"  Final model   → {MODEL_PATH}")
    logger.info(f"  Best model    → {BEST_MODEL_PATH}")
    logger.info(f"  Label mapping → {LABEL_MAP_PATH}")
    logger.info(f"  Metadata      → {MODEL_METADATA_PATH}")
    logger.info(f"  History JSON  → {HISTORY_PATH}")
    logger.info(f"  Accuracy plot → {PLOTS_DIR / 'accuracy.png'}")
    logger.info(f"  Loss plot     → {PLOTS_DIR / 'loss.png'}")
    logger.info("=" * 60)


if __name__ == '__main__':
    train()
