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
    raw = uuid.uuid4().hex
    return f"{prefix}{raw[:40]}"


def wallet_hash(wallet: str) -> str:
    return hashlib.sha256(wallet.encode()).hexdigest()[:16]


def serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in doc.items():
        if k == "_id":
            continue
        if isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
