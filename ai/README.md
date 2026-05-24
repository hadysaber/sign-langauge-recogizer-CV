# Real-Time Sign Language Recognition System

A real-time sign language recognition system using MediaPipe keypoints, TensorFlow/Keras, and an LSTM sequence classifier.

The current vocabulary is:

```text
hello, thanks, iloveyou, my_name_is, hady, i_am_from, egypt
```

## Environment

Use the project virtual environment. Do not use the global Python install for this project.

```powershell
cd "D:\sign langauge project\ai"
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The tested environment uses:

```text
TensorFlow 2.16.1
NumPy 1.26.4
MediaPipe 0.10.14
```

## Workflow

### 1. Reset For Scratch Training

To delete collected keypoints, trained models, logs, and reports:

```powershell
.venv\Scripts\python.exe src\reset_project.py
```

For a non-interactive reset:

```powershell
.venv\Scripts\python.exe src\reset_project.py --yes
```

The reset utility recreates the empty `data/`, `models/`, and `reports/` folders after cleanup.

### 2. Data Collection

Record webcam gesture sequences for every configured class:

```powershell
.venv\Scripts\python.exe src\data_collection.py
```

Current collection settings:

```text
60 sequences per action
30 frames per sequence
258 MediaPipe features per frame
```

Saved keypoints are written to:

```text
data/extracted/<action>/<sequence>/<frame>.npy
```

Tips for better accuracy:

- Collect all classes in the same session style if possible.
- Keep hands clearly visible for the full gesture.
- Vary hand position, distance from camera, and signing speed.
- Use consistent lighting and avoid a busy background.
- Re-record weak classes such as `egypt`, `hady`, `my_name_is`, and `i_am_from` if evaluation shows confusion.

### 3. Training

Train a fresh LSTM model:

```powershell
.venv\Scripts\python.exe src\train.py
```

Training now uses:

- signer-relative landmark normalization
- hand-landmark quality filtering
- train-only augmentation
- separate train, validation, and final test splits
- early stopping and checkpointing by validation loss

Training outputs:

| Artifact | Path | Description |
|---|---|---|
| Final model | `models/sign_model.keras` | Final model after training completes |
| Best model | `models/sign_model_best.keras` | Best checkpoint by validation loss |
| Label mapping | `models/label_mapping.json` | Action-to-index mapping |
| Model metadata | `models/model_metadata.json` | Preprocessing and split settings |
| Training history | `reports/training_history.json` | Epoch-level metrics |
| Accuracy plot | `reports/plots/accuracy.png` | Train vs. validation accuracy |
| Loss plot | `reports/plots/loss.png` | Train vs. validation loss |
| TensorBoard logs | `models/Logs/` | TensorBoard event logs |

### 4. Evaluation

Evaluate the best saved model on the untouched test split:

```powershell
.venv\Scripts\python.exe src\evaluate.py
```

Evaluation outputs:

| Artifact | Path | Description |
|---|---|---|
| Confusion matrix | `reports/plots/confusion_matrix.png` | True vs. predicted classes |
| Metrics summary | `reports/metrics/evaluation_results.json` | Accuracy, precision, recall, and F1 |

Accuracy should be treated carefully if the test set is small. A high score on 30-60 samples per class is useful for a demo, but more data from more people and lighting conditions is needed for real-world robustness.

### 5. Real-Time Inference

Run the webcam app:

```powershell
.venv\Scripts\python.exe app.py
```

Controls:

```text
q - quit
r - reset sequence buffer
s - toggle prediction smoothing
```

The app loads `models/sign_model_best.keras` when available, applies the same normalization used during training, and warns if model metadata does not match the current config.

## Configuration

Edit `src/config.py` before collecting or training.

Important settings:

```python
ACTIONS = [
    'hello', 'thanks', 'iloveyou',
    'my_name_is', 'hady', 'i_am_from', 'egypt'
]

SEQUENCE_LENGTH = 30
NO_SEQUENCES = 60

VALIDATION_SIZE = 0.15
TEST_SIZE = 0.15

NORMALIZE_LANDMARKS = True
AUGMENT_TRAINING_DATA = True
AUGMENTATION_COPIES = 2
```

If you change `ACTIONS`, recollect data for all classes and retrain from scratch.

## Extending The Vocabulary

1. Add the new label to `ACTIONS` in `src/config.py`.
2. Run `src/reset_project.py --yes` if you want a clean dataset.
3. Collect data for every class with `src/data_collection.py`.
4. Train with `src/train.py`.
5. Evaluate with `src/evaluate.py`.

The model output layer and label mapping are tied to the exact `ACTIONS` list, so changing labels without retraining will break or reduce inference quality.

## Project Structure

```text
ai/
|-- app.py
|-- requirements.txt
|-- src/
|   |-- config.py
|   |-- data_collection.py
|   |-- dataset.py
|   |-- evaluate.py
|   |-- extract.py
|   |-- model.py
|   |-- reset_project.py
|   |-- smoothing.py
|   |-- train.py
|   `-- ui.py
|-- data/
|   |-- raw/
|   `-- extracted/
|-- models/
|   |-- sign_model.keras
|   |-- sign_model_best.keras
|   |-- label_mapping.json
|   |-- model_metadata.json
|   `-- Logs/
`-- reports/
    |-- training_history.json
    |-- plots/
    |   |-- accuracy.png
    |   |-- loss.png
    |   `-- confusion_matrix.png
    `-- metrics/
        `-- evaluation_results.json
```
