"""Composite risk scoring and explanations."""

from typing import Any


def compute_risk_score(fraud_probability: float, anomaly_score: float, graph_risk: float) -> float:
    score = 0.5 * fraud_probability * 100 + 0.3 * anomaly_score * 100 + 0.2 * graph_risk * 100
    return round(min(max(score, 0), 100), 2)


def risk_level(score: float) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def build_explanation(features: dict, fraud_probability: float, anomaly_score: float, graph_flags: list[str]) -> list[str]:
    reasons = []
    if features.get("frequency", 0) > 15:
        reasons.append("High risk due to abnormal transaction frequency")
    if features.get("wallet_age_days", 999) < 14:
        reasons.append("New wallet with limited on-chain history")
    if features.get("num_receivers", 0) > 5:
        reasons.append("Unusual number of recipient addresses detected")
    if features.get("time_gap_hours", 999) < 1:
        reasons.append("Rapid successive transactions within short time window")
    if features.get("amount", 0) > 50000:
        reasons.append("Large transaction amount exceeds typical profile")
    if features.get("is_round_amount", 0) == 1 and features.get("amount", 0) > 10000:
        reasons.append("Round-number transfer pattern common in laundering")
    if anomaly_score > 0.7:
        reasons.append("ML anomaly detector flagged statistical outlier")
    if fraud_probability > 0.75:
        reasons.append("Supervised model indicates high fraud probability")
    reasons.extend(graph_flags)
    return reasons[:6] if reasons else ["Transaction appears within normal behavioral bounds"]


def analyze_result(tx, features, fraud_probability, anomaly_score, is_anomaly, graph_risk, graph_flags) -> dict[str, Any]:
    risk_score = compute_risk_score(fraud_probability, anomaly_score, graph_risk)
    level = risk_level(risk_score)
    return {
        "transaction_id": tx.get("transaction_id"),
        "wallet_from": tx.get("wallet_from"),
        "wallet_to": tx.get("wallet_to"),
        "amount": float(tx.get("amount", 0)),
        "symbol": tx.get("symbol", "BTC"),
        "risk_score": risk_score,
        "risk_level": level,
        "fraud_probability": round(float(fraud_probability), 4),
        "anomaly_score": round(float(anomaly_score), 4),
        "is_anomaly": bool(is_anomaly),
        "graph_risk": round(float(graph_risk), 4),
        "explanations": build_explanation(features, fraud_probability, anomaly_score, graph_flags),
        "features": {k: float(v) for k, v in features.items()},
        "timestamp": tx.get("timestamp"),
    }
