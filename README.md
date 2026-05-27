# AI Crypto Fraud Intelligence Platform

Production-style full-stack system for detecting fraudulent crypto transactions using live market data, machine learning, graph analysis, and a real-time dashboard.

## Features

- **Live data**: Binance prices via `ccxt` (mock fallback offline)
- **ML stack**: Random Forest + XGBoost ensemble, Isolation Forest anomalies
- **Graph analysis**: NetworkX wallet graphs, cluster & centrality detection
- **Risk scoring**: 0–100 composite score with explainable factors
- **Real-time**: WebSocket fraud alert stream
- **Dashboard**: Dark-themed React UI with charts, filters, CSV export

## Tech Stack

| Layer | Stack |
|-------|--------|
| Frontend | React (Vite), TailwindCSS, Chart.js, Recharts |
| Backend | FastAPI, Python |
| Database | MongoDB (optional — in-memory fallback) |
| ML | scikit-learn, XGBoost, Isolation Forest |
| Other | ccxt, networkx, WebSockets |

## Project Structure

```
crypto-fraud-platform/
├── backend/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── database/
│   └── utils/
├── frontend/
│   └── src/
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/live-price` | Live crypto price + 24h history |
| GET | `/api/transactions` | Scored transactions (`?risk=high\|medium\|low`) |
| POST | `/api/analyze` | Analyze a single transaction |
| POST | `/api/analyze/batch` | Generate & analyze mock batch |
| GET | `/api/fraud-alerts` | Fraud alert feed |
| GET | `/api/graph` | Wallet graph visualization data |
| GET | `/api/analytics` | Risk analytics aggregates |
| GET | `/api/export/csv` | Export report (optional `?risk=`) |
| WS | `/ws/alerts` | Real-time alert stream |

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (optional — app runs without it)

### Backend

```bash
cd crypto-fraud-platform
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### MongoDB (optional)

```bash
# Copy env and start MongoDB locally
cp .env.example .env
```

Without MongoDB, data is stored in memory and resets on restart.

## Usage

1. Open the **Dashboard** — live price chart, risk meter, fraud alerts (WebSocket).
2. Click **Run Fraud Scan** to analyze new mock transactions.
3. **Transactions** — filter by risk level, export CSV.
4. **Wallet Graph** — visualize connections and suspicious clusters.
5. **Risk Analytics** — fraud vs safe pie chart, risk distribution.

### Analyze custom transaction

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150000,
    "frequency": 45,
    "wallet_age_days": 3,
    "num_receivers": 20,
    "time_gap_hours": 0.2
  }'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection |
| `MONGO_DB` | `crypto_fraud_intel` | Database name |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |

## License

MIT — for portfolio and educational use.
