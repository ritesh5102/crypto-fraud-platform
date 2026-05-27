"""MongoDB connection and collection helpers."""

import os
from typing import Any, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

_client: Optional[MongoClient] = None
_db: Optional[Database] = None

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "crypto_fraud_intel")


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
    return _db


def get_collection(name: str) -> Collection:
    return get_db()[name]


def ping() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False


def insert_transaction(doc: dict[str, Any]) -> str:
    result = get_collection("transactions").insert_one(doc)
    return str(result.inserted_id)


def insert_alert(doc: dict[str, Any]) -> str:
    result = get_collection("fraud_alerts").insert_one(doc)
    return str(result.inserted_id)


def _sanitize(doc: dict) -> dict:
    """Convert numpy/Mongo types to JSON-serializable Python types."""
    out = {}
    for k, v in doc.items():
        if k == "_id":
            continue
        if hasattr(v, "item"):  # numpy scalar
            v = v.item()
        if isinstance(v, dict):
            v = _sanitize(v)
        out[k] = v
    return out


def get_transactions(limit: int = 100, risk_filter: Optional[str] = None) -> list[dict]:
    query: dict = {}
    if risk_filter == "high":
        query["risk_level"] = "high"
    elif risk_filter == "medium":
        query["risk_level"] = "medium"
    elif risk_filter == "low":
        query["risk_level"] = "low"

    cursor = (
        get_collection("transactions")
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return [_sanitize(d) for d in cursor]


def get_alerts(limit: int = 50) -> list[dict]:
    cursor = (
        get_collection("fraud_alerts")
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return list(cursor)
