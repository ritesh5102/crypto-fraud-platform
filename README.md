# AI Crypto Fraud Intelligence Platform

Production-ready full-stack system for detecting fraudulent crypto transactions using live market data, machine learning, graph analysis, and a real-time dashboard.

## Production readiness

| Area | Status |
|------|--------|
| Docker + Compose | Multi-service stack (MongoDB, API, Nginx) |
| Environment config | `pydantic-settings`, `.env` support |
| Security | CORS, rate limiting, security headers, HSTS (prod) |
| Observability | Structured logging, `/health` endpoints |
| CI/CD | GitHub Actions (backend, frontend, Docker build) |
| Resilience | In-memory fallback if MongoDB unavailable |
| Frontend | Nginx reverse proxy, API + WebSocket proxy |

## Quick start (Docker — recommended)

```bash
cd crypto-fraud-platform
cp .env.example .env
docker compose up --build -d
```

Open **http://localhost** (frontend) · API **http://localhost:8000/health**

## Local development

**Backend:**
```bash
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/live-price` | Live price + 24h OHLCV |
| GET | `/api/transactions?risk=high` | Scored transactions |
| POST | `/api/analyze` | Analyze transaction |
| GET | `/api/fraud-alerts` | Alert feed |
| GET | `/api/graph` | Wallet graph |
| GET | `/api/export/csv` | Export report |
| WS | `/ws/alerts` | Real-time alerts |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Set `production` for hardened mode |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed origins (comma-separated) |
| `RATE_LIMIT` | `60/minute` | API rate limit |

## Tech stack

FastAPI · React · Vite · TailwindCSS · MongoDB · scikit-learn · XGBoost · NetworkX · ccxt · WebSockets

## License

MIT
