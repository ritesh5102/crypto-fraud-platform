"""MongoDB connection and collection helpers."""

from typing import Any, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from config import get_settings
from utils.helpers import to_json_safe

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[get_settings().mongo_db]
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


def get_transactions(limit: int = 100, risk_filter: Optional[str] = None) -> list[dict]:
    query: dict = {}
    if risk_filter in ("high", "medium", "low"):
        query["risk_level"] = risk_filter

    cursor = (
        get_collection("transactions")
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return [to_json_safe(d) for d in cursor]


def get_alerts(limit: int = 50) -> list[dict]:
    cursor = (
        get_collection("fraud_alerts")
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return [to_json_safe(d) for d in cursor]
