"""Feature engineering for fraud detection models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class TransactionFeatures:
    amount: float
    frequency: float
    wallet_age_days: float
    num_receivers: int
    time_gap_hours: float
    hour_of_day: int
    is_round_amount: int

    def to_array(self) -> list[float]:
        return [
            self.amount,
            self.frequency,
            self.wallet_age_days,
            float(self.num_receivers),
            self.time_gap_hours,
            float(self.hour_of_day),
            float(self.is_round_amount),
        ]

    def to_dict(self) -> dict[str, float]:
        return {
            "amount": self.amount,
            "frequency": self.frequency,
            "wallet_age_days": self.wallet_age_days,
            "num_receivers": float(self.num_receivers),
            "time_gap_hours": self.time_gap_hours,
            "hour_of_day": float(self.hour_of_day),
            "is_round_amount": float(self.is_round_amount),
        }


FEATURE_NAMES = [
    "amount",
    "frequency",
    "wallet_age_days",
    "num_receivers",
    "time_gap_hours",
    "hour_of_day",
    "is_round_amount",
]


def extract_features(tx: dict[str, Any], history: list[dict] | None = None) -> TransactionFeatures:
    """Extract ML features from a transaction and optional wallet history."""
    history = history or []
    amount = float(tx.get("amount", 0))
    timestamp = tx.get("timestamp")
    if isinstance(timestamp, str):
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            ts = datetime.utcnow()
    elif isinstance(timestamp, datetime):
        ts = timestamp
    else:
        ts = datetime.utcnow()

    wallet_age = float(tx.get("wallet_age_days", 30))
    num_receivers = int(tx.get("num_receivers", 1))
    frequency = float(tx.get("frequency", len(history) + 1))

    time_gap = float(tx.get("time_gap_hours", 24.0))
    if history:
        prev = history[0].get("timestamp")
        if isinstance(prev, str):
            try:
                prev_ts = datetime.fromisoformat(prev.replace("Z", "+00:00"))
                time_gap = max((ts - prev_ts).total_seconds() / 3600, 0.01)
            except ValueError:
                pass

    is_round = 1 if amount > 0 and amount % 1000 == 0 else 0

    return TransactionFeatures(
        amount=amount,
        frequency=frequency,
        wallet_age_days=wallet_age,
        num_receivers=num_receivers,
        time_gap_hours=time_gap,
        hour_of_day=ts.hour,
        is_round_amount=is_round,
    )
