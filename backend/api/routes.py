"""REST API route handlers."""

import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import get_settings
from database import mongodb
from services.anomaly_detection import AnomalyDetector
from services.data_service import fetch_live_price, fetch_price_history, generate_batch, generate_mock_transaction
from services.feature_engineering import extract_features
from services.fraud_model import fraud_model, _generate_synthetic_data
from services.graph_analysis import graph_analyzer
from services.risk_scoring import analyze_result
from utils.helpers import generate_tx_id, utc_now_iso

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api")

_anomaly_detector = AnomalyDetector()
_in_memory_tx: list[dict] = []
_in_memory_alerts: list[dict] = []


def _init_ml():
    fraud_model.ensure_trained()
    import numpy as np
    X, _ = _generate_synthetic_data(500)
    _anomaly_detector.fit(X)


def seed_initial_data():
    _init_ml()
    for tx in generate_batch(30, fraud_bias=0.3):
        _analyze_transaction(tx)
    logger.info("Seeded %d transactions", len(_in_memory_tx))


def _store_tx(record: dict) -> None:
    _in_memory_tx.insert(0, record)
    if len(_in_memory_tx) > 500:
        _in_memory_tx.pop()
    try:
        if mongodb.ping():
            mongodb.insert_transaction(record)
    except Exception as e:
        logger.debug("MongoDB insert skipped: %s", e)


def _store_alert(alert: dict) -> None:
    _in_memory_alerts.insert(0, alert)
    if len(_in_memory_alerts) > 200:
        _in_memory_alerts.pop()
    try:
        if mongodb.ping():
            mongodb.insert_alert(alert)
    except Exception:
        pass


def _analyze_transaction(tx: dict) -> dict:
    features = extract_features(tx)
    feat_arr, feat_dict = features.to_array(), features.to_dict()
    fraud_prob = fraud_model.predict_proba(feat_arr)
    anomaly_score, is_anomaly = _anomaly_detector.predict_score(feat_arr)
    graph_analyzer.add_transaction(tx["wallet_from"], tx["wallet_to"], float(tx["amount"]), tx["transaction_id"])
    graph_risk, graph_flags = graph_analyzer.wallet_risk(tx["wallet_from"])
    result = analyze_result(tx, feat_dict, fraud_prob, anomaly_score, is_anomaly, graph_risk, graph_flags)
    record = {**tx, **result}
    _store_tx(record)
    if result["risk_level"] in ("high", "medium") and result["risk_score"] >= 40:
        alert = {
            "alert_id": f"alert_{tx['transaction_id']}", "transaction_id": tx["transaction_id"],
            "risk_score": result["risk_score"], "risk_level": result["risk_level"],
            "message": result["explanations"][0] if result["explanations"] else "Suspicious activity",
            "wallet_from": tx["wallet_from"], "amount": tx["amount"], "symbol": tx.get("symbol", "BTC"),
            "timestamp": utc_now_iso(),
        }
        _store_alert(alert)
        result["alert"] = alert
    return record


class AnalyzeRequest(BaseModel):
    transaction_id: Optional[str] = None
    wallet_from: Optional[str] = None
    wallet_to: Optional[str] = None
    amount: float = Field(..., gt=0)
    symbol: str = "BTC"
    frequency: float = 1.0
    wallet_age_days: float = 30.0
    num_receivers: int = 1
    time_gap_hours: float = 24.0


@router.get("/health")
async def health():
    return {"status": "ok", "mongodb": mongodb.ping(), "transactions_cached": len(_in_memory_tx),
            "environment": get_settings().environment, "timestamp": utc_now_iso()}


@router.get("/live-price")
@limiter.limit("60/minute")
async def live_price(request: Request, symbol: str = Query("BTC/USDT")):
    return {"current": fetch_live_price(symbol), "history": fetch_price_history(symbol, 24)}


@router.get("/transactions")
async def transactions(limit: int = Query(50, ge=1, le=200), risk: Optional[str] = Query(None)):
    try:
        if mongodb.ping():
            data = mongodb.get_transactions(limit, risk)
            if data:
                return {"transactions": data, "count": len(data)}
    except Exception:
        pass
    txs = _in_memory_tx[:limit]
    if risk:
        txs = [t for t in txs if t.get("risk_level") == risk]
    return {"transactions": txs, "count": len(txs)}


@router.post("/analyze")
@limiter.limit("30/minute")
async def analyze(request: Request, body: AnalyzeRequest):
    tx = {
        "transaction_id": body.transaction_id or generate_tx_id(),
        "wallet_from": body.wallet_from or "0x" + "a" * 40,
        "wallet_to": body.wallet_to or "0x" + "b" * 40,
        "amount": body.amount, "symbol": body.symbol, "frequency": body.frequency,
        "wallet_age_days": body.wallet_age_days, "num_receivers": body.num_receivers,
        "time_gap_hours": body.time_gap_hours, "timestamp": utc_now_iso(),
    }
    return _analyze_transaction(tx)


@router.post("/analyze/batch")
async def analyze_batch(count: int = Query(5, ge=1, le=20)):
    results = [_analyze_transaction(tx) for tx in generate_batch(count)]
    return {"analyzed": len(results), "transactions": results}


@router.get("/fraud-alerts")
async def fraud_alerts(limit: int = Query(30, ge=1, le=100)):
    try:
        if mongodb.ping():
            data = mongodb.get_alerts(limit)
            if data:
                return {"alerts": data, "count": len(data)}
    except Exception:
        pass
    return {"alerts": _in_memory_alerts[:limit], "count": min(len(_in_memory_alerts), limit)}


@router.get("/graph")
async def wallet_graph():
    return graph_analyzer.to_visualization()


@router.get("/analytics")
async def analytics():
    txs = _in_memory_tx or []
    if not txs:
        return {"fraud_vs_safe": [], "risk_distribution": [], "avg_risk": 0, "total_transactions": 0}
    fraud = sum(1 for t in txs if t.get("risk_level") == "high")
    medium = sum(1 for t in txs if t.get("risk_level") == "medium")
    safe = len(txs) - fraud - medium
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for t in txs:
        s = t.get("risk_score", 0)
        key = "81-100" if s > 80 else "61-80" if s > 60 else "41-60" if s > 40 else "21-40" if s > 20 else "0-20"
        buckets[key] += 1
    return {
        "fraud_vs_safe": [{"name": "High Risk", "value": fraud}, {"name": "Medium Risk", "value": medium},
                          {"name": "Low Risk", "value": safe}],
        "risk_distribution": [{"range": k, "count": v} for k, v in buckets.items()],
        "avg_risk": round(sum(t.get("risk_score", 0) for t in txs) / len(txs), 2),
        "total_transactions": len(txs),
    }


@router.get("/export/csv")
async def export_csv(risk: Optional[str] = None):
    txs = [t for t in _in_memory_tx if not risk or t.get("risk_level") == risk]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "transaction_id", "wallet_from", "wallet_to", "amount", "symbol",
        "risk_score", "risk_level", "fraud_probability", "timestamp",
    ], extrasaction="ignore")
    writer.writeheader()
    writer.writerows(txs)
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=fraud_report.csv"})
