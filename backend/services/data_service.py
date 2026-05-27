"""Live market data (ccxt) and mock blockchain transactions."""

import random
from datetime import datetime, timedelta, timezone
from typing import Any

from utils.helpers import generate_tx_id, generate_wallet_id, utc_now_iso

_ccxt = None
_wallet_pool: list[str] = []


def _get_exchange():
    global _ccxt
    if _ccxt is None:
        try:
            import ccxt
            _ccxt = ccxt.binance({"enableRateLimit": True})
        except Exception:
            _ccxt = False
    return _ccxt if _ccxt is not False else None


def fetch_live_price(symbol: str = "BTC/USDT") -> dict[str, Any]:
    exchange = _get_exchange()
    if exchange:
        try:
            ticker = exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol, "price": ticker.get("last") or ticker.get("close"),
                "bid": ticker.get("bid"), "ask": ticker.get("ask"),
                "volume_24h": ticker.get("quoteVolume"), "change_24h": ticker.get("percentage"),
                "high_24h": ticker.get("high"), "low_24h": ticker.get("low"),
                "timestamp": utc_now_iso(), "source": "binance",
            }
        except Exception:
            pass
    base_prices = {"BTC/USDT": 67500, "ETH/USDT": 3200, "BNB/USDT": 590}
    price = round(base_prices.get(symbol, 1000) * (1 + random.uniform(-0.02, 0.02)), 2)
    return {"symbol": symbol, "price": price, "bid": round(price * 0.999, 2), "ask": round(price * 1.001, 2),
            "volume_24h": random.uniform(1e8, 5e8), "change_24h": round(random.uniform(-5, 5), 2),
            "high_24h": round(price * 1.03, 2), "low_24h": round(price * 0.97, 2),
            "timestamp": utc_now_iso(), "source": "mock"}


def fetch_price_history(symbol: str = "BTC/USDT", points: int = 24) -> list[dict]:
    exchange = _get_exchange()
    if exchange:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=points)
            return [{"time": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "volume": r[5]} for r in ohlcv]
        except Exception:
            pass
    base = fetch_live_price(symbol)["price"]
    history, price, now = [], base, datetime.now(timezone.utc)
    for i in range(points):
        ts = now - timedelta(hours=points - i)
        change = random.uniform(-0.015, 0.015)
        o, c = price, round(price * (1 + change), 2)
        history.append({"time": int(ts.timestamp() * 1000), "open": o, "high": round(max(o, c) * 1.005, 2),
                        "low": round(min(o, c) * 0.995, 2), "close": c, "volume": random.uniform(100, 5000)})
        price = c
    return history


def _ensure_wallets(n: int = 50) -> list[str]:
    global _wallet_pool
    while len(_wallet_pool) < n:
        _wallet_pool.append(generate_wallet_id())
    return _wallet_pool


def generate_mock_transaction(fraud_bias: float = 0.2) -> dict[str, Any]:
    wallets = _ensure_wallets(50)
    is_fraud = random.random() < fraud_bias
    if is_fraud:
        wf, wt = random.choice(wallets[:10]), random.choice(wallets)
        amount, freq, age, recv, gap = round(random.uniform(25000, 200000), 2), random.uniform(20, 80), random.uniform(0.5, 10), random.randint(8, 30), random.uniform(0.05, 0.8)
    else:
        wf, wt = random.choice(wallets), random.choice(wallets)
        amount, freq, age, recv, gap = round(random.uniform(50, 8000), 2), random.uniform(1, 8), random.uniform(60, 400), random.randint(1, 2), random.uniform(6, 48)
    return {
        "transaction_id": generate_tx_id(), "wallet_from": wf, "wallet_to": wt, "amount": amount,
        "symbol": random.choice(["BTC", "ETH", "USDT", "BNB"]), "frequency": round(freq, 2),
        "wallet_age_days": round(age, 2), "num_receivers": recv, "time_gap_hours": round(gap, 4),
        "timestamp": utc_now_iso(), "block_number": random.randint(18_000_000, 19_000_000),
        "gas_used": random.randint(21000, 150000),
    }


def generate_batch(count: int = 10, fraud_bias: float = 0.25) -> list[dict]:
    return [generate_mock_transaction(fraud_bias) for _ in range(count)]
