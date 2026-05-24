"""
Standalone evaluation script for the Sign Language Recognition model.

Loads the trained LSTM model and test data, then generates:
  - Overall test accuracy
  - Per-class precision, recall, and F1-score
  - Confusion matrix image
  - Evaluation summary JSON

Usage:
    python src/evaluate.py
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
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import tensorflow as tf
    from sklearn.metrics import (
        classification_report, confusion_matrix, accuracy_score
    )
except ImportError as e:
    logger.error(
        f"Missing critical dependency: {e.name}. "
        "Please run 'pip install -r requirements.txt'"
    )
    sys.exit(1)

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.dataset import load_data
from src.config import (
    MODEL_PATH, BEST_MODEL_PATH, ACTIONS,
    PLOTS_DIR, METRICS_DIR, MODEL_METADATA_PATH,
    NORMALIZE_LANDMARKS
)


# ──────────────────────────────────────────────
# Confusion Matrix Plot
# ──────────────────────────────────────────────

def plot_confusion_matrix(cm: np.ndarray, class_names: list, out_path: Path) -> None:
    """
    Generates a publication-quality confusion matrix heatmap and saves it.

    Args:
        cm:           The confusion matrix (n_classes × n_classes).
        class_names:  List of class label strings.
        out_path:     Destination file path for the image.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=class_names,
        yticklabels=class_names,
        ylabel='True Label',
        xlabel='Predicted Label',
        title='Confusion Matrix'
    )
    ax.title.set_fontsize(14)
    ax.title.set_fontweight('bold')

    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=11)
    plt.setp(ax.get_yticklabels(), fontsize=11)

    # Annotate each cell with the count
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha='center', va='center', fontsize=13,
                    color='white' if cm[i, j] > thresh else 'black')

    plt.tight_layout()
    plt.savefig(str(out_path), dpi=150)
    plt.close()
    logger.info(f"Confusion matrix saved → {out_path}")


# ──────────────────────────────────────────────
# Main Evaluation Function
# ──────────────────────────────────────────────

def evaluate() -> None:
    """
    Runs the full evaluation pipeline:
      1. Load test data
      2. Load trained model weights
      3. Generate predictions
      4. Compute and save metrics
      5. Generate confusion matrix plot
    """
    logger.info("=" * 60)
    logger.info("  Sign Language LSTM — Evaluation Pipeline")
    logger.info("=" * 60)

    # ── 1. Load Dataset ──
    logger.info("Loading dataset (using the final untouched test split)...")
    _, _, X_test, _, _, y_test = load_data(augment_train=False)
    logger.info(f"Test set: {X_test.shape[0]} samples")

    # ── 2. Load Model ──
    # Prefer the best checkpoint; fall back to the final model
    model_path = BEST_MODEL_PATH if BEST_MODEL_PATH.exists() else MODEL_PATH
    if not model_path.exists():
        logger.error(
            f"No trained model found at {BEST_MODEL_PATH} or {MODEL_PATH}. "
            "Please run 'python src/train.py' first."
        )
        sys.exit(1)

    logger.info(f"Loading model from → {model_path}")
    model = tf.keras.models.load_model(str(model_path))
    if MODEL_METADATA_PATH.exists():
        with open(MODEL_METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        if metadata.get("normalize_landmarks") != NORMALIZE_LANDMARKS:
            logger.warning(
                "Model preprocessing metadata differs from current config. "
                "Retrain before trusting this evaluation."
            )
    else:
        logger.warning(
            "Model metadata is missing. Retrain before trusting this evaluation "
            "with the current preprocessing settings."
        )

    # ── 3. Generate Predictions ──
    logger.info("Running inference on test set...")
    y_pred_proba = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_proba, axis=1)
    y_true = np.argmax(y_test, axis=1)

    # ── 4. Compute Metrics ──
    logger.info("-" * 60)
    overall_acc = accuracy_score(y_true, y_pred)
    logger.info(f"Overall Test Accuracy: {overall_acc:.4f} ({overall_acc*100:.1f}%)")

    # Classification report (console + dict)
    report_str = classification_report(
        y_true, y_pred, target_names=ACTIONS, digits=4, zero_division=0
    )
    report_dict = classification_report(
        y_true, y_pred, target_names=ACTIONS, output_dict=True, zero_division=0
    )
    logger.info(f"\nClassification Report:\n{report_str}")

    # ── 5. Confusion Matrix ──
    cm = confusion_matrix(y_true, y_pred)
    cm_path = PLOTS_DIR / "confusion_matrix.png"
    plot_confusion_matrix(cm, ACTIONS, cm_path)

    # ── 6. Save Evaluation Results ──
    results = {
        "timestamp": datetime.now().isoformat(),
        "model_path": str(model_path),
        "test_samples": int(X_test.shape[0]),
        "overall_accuracy": round(float(overall_acc), 4),
        "per_class": {
            action: {
                "precision": round(report_dict[action]["precision"], 4),
                "recall":    round(report_dict[action]["recall"], 4),
                "f1_score":  round(report_dict[action]["f1-score"], 4),
                "support":   int(report_dict[action]["support"]),
            }
            for action in ACTIONS
        },
        "confusion_matrix": cm.tolist()
    }

    results_path = METRICS_DIR / "evaluation_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Evaluation results saved → {results_path}")

    # ── 7. Summary ──
    logger.info("=" * 60)
    logger.info("Evaluation complete!")
    logger.info(f"  Accuracy          → {overall_acc*100:.1f}%")
    logger.info(f"  Confusion matrix  → {cm_path}")
    logger.info(f"  Metrics JSON      → {results_path}")
    logger.info("=" * 60)


if __name__ == '__main__':
    evaluate()
