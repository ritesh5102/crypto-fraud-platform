"""Shared utility helpers."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def generate_tx_id() -> str:
    return f"tx_{uuid.uuid4().hex[:12]}"


def generate_wallet_id(prefix: str = "0x") -> str:
    return f"{prefix}{uuid.uuid4().hex[:40]}"


def to_json_safe(obj: Any) -> Any:
    """Convert numpy/Mongo types to JSON-serializable values."""
    if hasattr(obj, "item"):
        return obj.item()
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj
