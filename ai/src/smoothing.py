"""
Logic for smoothing model predictions over a sliding window.
"""

from collections import deque, Counter
from typing import Optional

class PredictionSmoother:
    def __init__(self, window_size: int = 5):
        """
        Maintains a rolling history of predictions to avoid UI flickering.
        
        Args:
            window_size (int): The number of frames to retain for the consensus vote.
        """
        self.history = deque(maxlen=window_size)
        self.last_stable: Optional[str] = None
        
    def add_prediction(self, label: str) -> None:
        """Adds a new prediction to the history buffer."""
        self.history.append(label)
        
    def get_stable_prediction(self) -> Optional[str]:
        """
        Calculates the most frequent label in the current history window.
        If a label has a strict majority, it becomes the new stable prediction.
        
        Returns:
            Optional[str]: The smoothed, stable prediction.
        """
        if not self.history:
            return None
            
        counts = Counter(self.history)
        most_common_label, count = counts.most_common(1)[0]
        
        # Require a strict majority (over 50%)
        if count > len(self.history) / 2:
            self.last_stable = most_common_label
            
        return self.last_stable
        
    def reset(self) -> None:
        """Clears the smoothing buffers."""
        self.history.clear()
        self.last_stable = None
