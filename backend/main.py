"""
AI Crypto Fraud Intelligence Platform — FastAPI Backend
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend root is on path
BACKEND_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_ROOT))

from api.routes import router, seed_initial_data, _in_memory_alerts
from api.websocket import ws_manager, alert_stream_task
from services.data_service import generate_mock_transaction

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_data()

    async def produce_alert():
        from api.routes import _analyze_transaction
        from services.data_service import generate_mock_transaction

        tx = generate_mock_transaction(fraud_bias=0.35)
        result = _analyze_transaction(tx)
        return result.get("alert")

    task = asyncio.create_task(alert_stream_task(produce_alert, interval=10.0))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI Crypto Fraud Intelligence Platform",
    description="Real-time crypto fraud detection with ML, graph analysis, and live market data",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to fraud alert stream",
            "alerts_count": len(_in_memory_alerts),
        })
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "service": "AI Crypto Fraud Intelligence Platform",
        "docs": "/docs",
        "endpoints": [
            "GET /api/live-price",
            "GET /api/transactions",
            "POST /api/analyze",
            "GET /api/fraud-alerts",
            "GET /api/graph",
            "GET /api/analytics",
            "GET /api/export/csv",
            "WS /ws/alerts",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
