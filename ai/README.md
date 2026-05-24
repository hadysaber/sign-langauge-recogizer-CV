# Real-Time Sign Language Recognition System

A production-quality, minimal real-time sign language recognition system using MediaPipe and TensorFlow.

## Setup

1. Create a virtual environment and activate it.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Workflow

### 1. Data Collection
Activate the webcam and record gesture sequences for each sign class.
```bash
python src/data_collection.py
```
- Captures 30 sequences × 30 frames per action.
- Saved as `.npy` keypoint arrays in `data/extracted/<action>/<sequence>/`.

#### Tips for Better Accuracy
- **Minimum 30 sequences per class** — 40+ is recommended for stable results.
- **Consistent lighting and background** — avoid drastic changes between sessions.
- **Vary hand position slightly** between sequences so the model generalizes.
- **Keep your hands clearly visible** — the model relies on hand landmarks above all.
- **Avoid signs that look identical at the start** — the LSTM needs distinguishable motion.
- **Damaged sequences** (>25% missing frames) are automatically skipped during training.

### 2. Training
Train the LSTM model on the collected data.
```bash
python src/train.py
```

#### Training Outputs
| Artifact | Path | Description |
|---|---|---|
| Final model | `models/sign_model.keras` | Model saved after training completes |
| Best model | `models/sign_model_best.keras` | Checkpoint with highest validation accuracy |
| Label mapping | `models/label_mapping.json` | `{action: index}` used during training |
| Training history | `reports/training_history.json` | Epoch-by-epoch loss and accuracy |
| Accuracy plot | `reports/plots/accuracy.png` | Train vs. validation accuracy curves |
| Loss plot | `reports/plots/loss.png` | Train vs. validation loss curves |
| TensorBoard logs | `models/Logs/` | Viewable with `tensorboard --logdir models/Logs` |

#### Configuration
Edit `src/config.py` to tune hyperparameters before training:
```python
EPOCHS = 250           # maximum training epochs
BATCH_SIZE = 16        # samples per gradient update
LEARNING_RATE = 0.001  # Adam optimizer learning rate
TEST_SIZE = 0.10       # fraction held out for testing
ES_PATIENCE = 15       # early-stopping patience (epochs)
```

### 3. Evaluation
Run the standalone evaluation script after training to generate metrics and visualizations.
```bash
python src/evaluate.py
```

#### Evaluation Outputs
| Artifact | Path | Description |
|---|---|---|
| Confusion matrix | `reports/plots/confusion_matrix.png` | Heatmap of true vs. predicted labels |
| Metrics summary | `reports/metrics/evaluation_results.json` | Accuracy, per-class precision/recall/F1 |

#### How to Interpret Results
- **Accuracy** — overall percentage of correctly classified test sequences.
- **Precision** — of all sequences predicted as class X, how many were actually X.
- **Recall** — of all actual class X sequences, how many were correctly predicted.
- **F1-Score** — harmonic mean of precision and recall (balanced metric).
- **Confusion Matrix** — rows are true labels, columns are predictions. Diagonal = correct.

### 4. Real-Time Inference
Start the main application to recognize signs in real-time via webcam.
```bash
python app.py
```
- Press **q** to quit, **r** to reset the buffer, **s** to toggle prediction smoothing.

### 5. Reset Project
To wipe all collected data, trained models, and generated reports before starting fresh:
```bash
python src/reset_project.py
```
The script will show exactly what will be deleted and ask for confirmation before proceeding. After reset, all required empty directories are recreated automatically.

## Extending the Vocabulary

To add new sign labels to the system:

1. **Edit `src/config.py`** — append your new labels to the `ACTIONS` list:
   ```python
   ACTIONS: List[str] = [
       'hello', 'thanks', 'iloveyou',
       'my_name_is', 'hady', 'i_am_from', 'egypt',
       'your_new_sign'  # ← add here
   ]
   ```

2. **Collect data for ALL classes** — run `python src/data_collection.py`. The script automatically creates folders for every label in `ACTIONS`.

3. **Retrain the model** — run `python src/train.py`. The LSTM output layer dynamically sizes itself to `len(ACTIONS)`, so no architecture changes are needed.

4. **Evaluate** — run `python src/evaluate.py` to verify performance on the new class set.

> **Why full retraining?** The model's output layer and label mapping are tied to the exact `ACTIONS` list. Changing `ACTIONS` without retraining will cause a shape mismatch. The inference script (`app.py`) will warn you if the saved label mapping doesn't match the current `ACTIONS`.

## Project Structure
```
sign-language-project/
├── app.py                      # Real-time webcam inference
├── requirements.txt            # Python dependencies
├── src/
│   ├── config.py               # All paths, hyperparams, and constants
│   ├── data_collection.py      # Webcam data capture
│   ├── dataset.py              # Data loading and preprocessing
│   ├── evaluate.py             # Standalone evaluation script
│   ├── extract.py              # MediaPipe landmark extraction
│   ├── model.py                # LSTM model architecture
│   ├── reset_project.py        # Project reset utility
│   ├── smoothing.py            # Prediction consensus smoother
│   ├── train.py                # Training orchestrator
│   └── ui.py                   # OpenCV UI overlay rendering
├── data/
│   ├── raw/                    # (reserved for raw video)
│   └── extracted/              # Keypoint .npy files per action
├── models/
│   ├── sign_model.keras        # Final trained model
│   ├── sign_model_best.keras   # Best validation checkpoint
│   ├── label_mapping.json      # Class label ↔ index mapping
│   └── Logs/                   # TensorBoard logs
└── reports/
    ├── training_history.json   # Epoch-level metrics
    ├── plots/
    │   ├── accuracy.png        # Accuracy curves
    │   ├── loss.png            # Loss curves
    │   └── confusion_matrix.png
    └── metrics/
        └── evaluation_results.json
```
