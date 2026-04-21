# Real-Time Sign Language Recognition System

A production-quality, minimal real-time sign language recognition system using MediaPipe and TensorFlow. 

## Setup

1. Create a virtual environment and activate it.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Data Collection
To train the model on new gestures, run the data collection script. It will activate the webcam and prompt you to perform gestures to record frame sequences.
```bash
python src/data_collection.py
```

### 2. Training
After gathering the dataset, train the LSTM model.
```bash
python src/train.py
```

### 3. Real-Time Inference
Start the main application to recognize signs in real-time.
```bash
python app.py
```
