"""Live market data (ccxt) and synthetic blockchain transaction generation."""

import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from utils.helpers import generate_tx_id, generate_wallet_id, utc_now_iso

# Lazy ccxt import — falls back to mock if unavailable
_ccxt = None


def _get_exchange():
    global _ccxt
    if _ccxt is None:
        try:
            import ccxt

            exchange = ccxt.binance({"enableRateLimit": True})
            _ccxt = exchange
        except Exception:
            _ccxt = False
    return _ccxt if _ccxt is not False else None


def fetch_live_price(symbol: str = "BTC/USDT") -> dict[str, Any]:
    exchange = _get_exchange()
    if exchange:
        try:
            ticker = exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "price": ticker.get("last") or ticker.get("close"),
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "volume_24h": ticker.get("quoteVolume"),
                "change_24h": ticker.get("percentage"),
                "high_24h": ticker.get("high"),
                "low_24h": ticker.get("low"),
                "timestamp": utc_now_iso(),
                "source": "binance",
            }
        except Exception as e:
            pass

    # Mock fallback
    base_prices = {"BTC/USDT": 67500, "ETH/USDT": 3200, "BNB/USDT": 590}
    base = base_prices.get(symbol, 1000)
    jitter = random.uniform(-0.02, 0.02)
    price = round(base * (1 + jitter), 2)
    return {
        "symbol": symbol,
        "price": price,
        "bid": round(price * 0.999, 2),
        "ask": round(price * 1.001, 2),
        "volume_24h": random.uniform(1e8, 5e8),
        "change_24h": round(random.uniform(-5, 5), 2),
        "high_24h": round(price * 1.03, 2),
        "low_24h": round(price * 0.97, 2),
        "timestamp": utc_now_iso(),
        "source": "mock",
    }


def fetch_price_history(symbol: str = "BTC/USDT", points: int = 24) -> list[dict]:
    exchange = _get_exchange()
    if exchange:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=points)
            return [
                {"time": row[0], "open": row[1], "high": row[2], "low": row[3], "close": row[4], "volume": row[5]}
                for row in ohlcv
            ]
        except Exception:
            pass

    # Mock OHLCV
    base = fetch_live_price(symbol)["price"]
    history = []
    now = datetime.now(timezone.utc)
    price = base
    for i in range(points):
        ts = now - timedelta(hours=points - i)
        change = random.uniform(-0.015, 0.015)
        open_p = price
        close_p = round(price * (1 + change), 2)
        high_p = round(max(open_p, close_p) * 1.005, 2)
        low_p = round(min(open_p, close_p) * 0.995, 2)
        history.append({
            "time": int(ts.timestamp() * 1000),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": random.uniform(100, 5000),
        })
        price = close_p
    return history


# In-memory wallet pool for realistic graph
_wallet_pool: list[str] = []


def _ensure_wallets(n: int = 50) -> list[str]:
    global _wallet_pool
    while len(_wallet_pool) < n:
        _wallet_pool.append(generate_wallet_id())
    return _wallet_pool


def generate_mock_transaction(fraud_bias: float = 0.2) -> dict[str, Any]:
    """Generate a realistic mock blockchain transaction."""
    wallets = _ensure_wallets(50)
    is_fraud = random.random() < fraud_bias

    if is_fraud:
        wallet_from = random.choice(wallets[:10])
        wallet_to = random.choice(wallets)
        amount = round(random.uniform(25000, 200000), 2)
        frequency = random.uniform(20, 80)
        wallet_age_days = random.uniform(0.5, 10)
        num_receivers = random.randint(8, 30)
        time_gap_hours = random.uniform(0.05, 0.8)
    else:
        wallet_from = random.choice(wallets)
        wallet_to = random.choice(wallets)
        amount = round(random.uniform(50, 8000), 2)
        frequency = random.uniform(1, 8)
        wallet_age_days = random.uniform(60, 400)
        num_receivers = random.randint(1, 2)
        time_gap_hours = random.uniform(6, 48)

    symbols = ["BTC", "ETH", "USDT", "BNB"]
    return {
        "transaction_id": generate_tx_id(),
        "wallet_from": wallet_from,
        "wallet_to": wallet_to,
        "amount": amount,
        "symbol": random.choice(symbols),
        "frequency": round(frequency, 2),
        "wallet_age_days": round(wallet_age_days, 2),
        "num_receivers": num_receivers,
        "time_gap_hours": round(time_gap_hours, 4),
        "timestamp": utc_now_iso(),
        "block_number": random.randint(18_000_000, 19_000_000),
        "gas_used": random.randint(21000, 150000),
    }


def generate_batch(count: int = 10, fraud_bias: float = 0.25) -> list[dict]:
    return [generate_mock_transaction(fraud_bias) for _ in range(count)]
