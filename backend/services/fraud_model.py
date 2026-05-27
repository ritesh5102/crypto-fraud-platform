"""Supervised fraud detection models (Random Forest + XGBoost)."""

import os
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
    """Generate synthetic labeled transaction data for training."""
    rng = np.random.default_rng(42)
    X, y = [], []

    for _ in range(n):
        is_fraud = rng.random() < 0.2
        if is_fraud:
            amount = rng.uniform(50000, 500000)
            frequency = rng.uniform(20, 100)
            wallet_age = rng.uniform(0, 7)
            receivers = int(rng.integers(10, 50))
            time_gap = rng.uniform(0.01, 0.5)
            hour = int(rng.integers(0, 6))
            round_amt = 1
        else:
            amount = rng.uniform(10, 5000)
            frequency = rng.uniform(1, 10)
            wallet_age = rng.uniform(30, 365)
            receivers = int(rng.integers(1, 3))
            time_gap = rng.uniform(12, 72)
            hour = int(rng.integers(8, 20))
            round_amt = int(rng.random() < 0.1)

        X.append([amount, frequency, wallet_age, receivers, time_gap, hour, round_amt])
        y.append(1 if is_fraud else 0)

    return np.array(X), np.array(y)


class FraudModelEnsemble:
    def __init__(self):
        self.rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        self.xgb = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            eval_metric="logloss",
            random_state=42,
        )
        self._trained = False

    def train(self) -> dict:
        X, y = _generate_synthetic_data(3000)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.rf.fit(X_train, y_train)
        self.xgb.fit(X_train, y_train)

        rf_acc = self.rf.score(X_test, y_test)
        xgb_acc = self.xgb.score(X_test, y_test)
        self._trained = True

        self._save_models()
        return {"rf_accuracy": round(rf_acc, 4), "xgb_accuracy": round(xgb_acc, 4)}

    def _save_models(self) -> None:
        with open(MODEL_DIR / "rf_model.pkl", "wb") as f:
            pickle.dump(self.rf, f)
        with open(MODEL_DIR / "xgb_model.pkl", "wb") as f:
            pickle.dump(self.xgb, f)

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
        if not self._trained:
            if not self._load_models():
                self.train()

    def predict_proba(self, features: list[float]) -> float:
        self.ensure_trained()
        X = np.array([features])
        rf_prob = self.rf.predict_proba(X)[0][1]
        xgb_prob = self.xgb.predict_proba(X)[0][1]
        return float(0.45 * rf_prob + 0.55 * xgb_prob)

    def feature_importance(self) -> dict[str, float]:
        self.ensure_trained()
        imp = self.rf.feature_importances_
        return {name: round(float(v), 4) for name, v in zip(FEATURE_NAMES, imp)}


# Singleton
fraud_model = FraudModelEnsemble()
