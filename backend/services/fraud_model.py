"""Supervised fraud detection (Random Forest + XGBoost)."""

import pickle
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from services.feature_engineering import FEATURE_NAMES

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


def _generate_synthetic_data(n: int = 2000) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    X, y = [], []
    for _ in range(n):
        is_fraud = rng.random() < 0.2
        if is_fraud:
            row = [rng.uniform(50000, 500000), rng.uniform(20, 100), rng.uniform(0, 7),
                   int(rng.integers(10, 50)), rng.uniform(0.01, 0.5), int(rng.integers(0, 6)), 1]
        else:
            row = [rng.uniform(10, 5000), rng.uniform(1, 10), rng.uniform(30, 365),
                   int(rng.integers(1, 3)), rng.uniform(12, 72), int(rng.integers(8, 20)),
                   int(rng.random() < 0.1)]
        X.append(row)
        y.append(1 if is_fraud else 0)
    return np.array(X), np.array(y)


class FraudModelEnsemble:
    def __init__(self):
        self.rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        self.xgb = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1,
                                 eval_metric="logloss", random_state=42)
        self._trained = False

    def train(self) -> dict:
        X, y = _generate_synthetic_data(3000)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.rf.fit(X_train, y_train)
        self.xgb.fit(X_train, y_train)
        self._trained = True
        with open(MODEL_DIR / "rf_model.pkl", "wb") as f:
            pickle.dump(self.rf, f)
        with open(MODEL_DIR / "xgb_model.pkl", "wb") as f:
            pickle.dump(self.xgb, f)
        return {"rf_accuracy": round(self.rf.score(X_test, y_test), 4),
                "xgb_accuracy": round(self.xgb.score(X_test, y_test), 4)}

    def _load_models(self) -> bool:
        rf_path, xgb_path = MODEL_DIR / "rf_model.pkl", MODEL_DIR / "xgb_model.pkl"
        if rf_path.exists() and xgb_path.exists():
            with open(rf_path, "rb") as f:
                self.rf = pickle.load(f)
            with open(xgb_path, "rb") as f:
                self.xgb = pickle.load(f)
            self._trained = True
            return True
        return False

    def ensure_trained(self) -> None:
        if not self._trained and not self._load_models():
            self.train()

    def predict_proba(self, features: list[float]) -> float:
        self.ensure_trained()
        X = np.array([features])
        return float(0.45 * self.rf.predict_proba(X)[0][1] + 0.55 * self.xgb.predict_proba(X)[0][1])


fraud_model = FraudModelEnsemble()
