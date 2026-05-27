"""Isolation Forest anomaly detection."""

import numpy as np
from sklearn.ensemble import IsolationForest

from services.feature_engineering import FEATURE_NAMES


class AnomalyDetector:
    def __init__(self, contamination: float = 0.15):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
        )
        self._fitted = False

    def fit(self, X: np.ndarray) -> None:
        self.model.fit(X)
        self._fitted = True

    def predict_score(self, features: list[float]) -> tuple[float, bool]:
        """Return anomaly score (0-1, higher = more anomalous) and is_anomaly flag."""
        if not self._fitted:
            return 0.0, False

        X = np.array([features])
        raw = self.model.decision_function(X)[0]
        # decision_function: negative = anomaly; normalize to 0-1
        score = float(1 / (1 + np.exp(raw * 2)))
        pred = self.model.predict(X)[0]
        is_anomaly = pred == -1
        return score, is_anomaly

    @property
    def feature_names(self) -> list[str]:
        return FEATURE_NAMES
