import { useEffect, useState, useCallback } from 'react'
import { api, createAlertWebSocket } from '../services/api'
import PriceChart from '../components/PriceChart'
import RiskMeter from '../components/RiskMeter'
import AlertsPanel from '../components/AlertsPanel'

export default function Dashboard() {
  const [price, setPrice] = useState(null)
  const [history, setHistory] = useState([])
  const [alerts, setAlerts] = useState([])
  const [liveAlert, setLiveAlert] = useState(null)
  const [avgRisk, setAvgRisk] = useState(0)
  const [symbol, setSymbol] = useState('BTC/USDT')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const [priceRes, alertsRes, analyticsRes] = await Promise.all([
        api.livePrice(symbol),
        api.fraudAlerts(20),
        api.analytics(),
      ])
      setPrice(priceRes.current)
      setHistory(priceRes.history || [])
      setAlerts(alertsRes.alerts || [])
      setAvgRisk(analyticsRes.avg_risk || 0)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [symbol])

  useEffect(() => {
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [load])

  useEffect(() => {
    const ws = createAlertWebSocket((msg) => {
      if (msg.type === 'fraud_alert' && msg.data) {
        setLiveAlert(msg.data)
        setAlerts((prev) => [msg.data, ...prev].slice(0, 30))
      }
    })
    return () => ws.close()
  }, [])

  const runScan = async () => {
    setLoading(true)
    await api.analyzeBatch(5)
    await load()
  }

  if (loading && !price) {
    return <div className="text-gray-500 animate-pulse">Loading intelligence feed…</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Fraud Intelligence Dashboard</h2>
          <p className="text-gray-500 text-sm mt-1">Live market data · ML risk scoring · Real-time alerts</p>
        </div>
        <div className="flex gap-2">
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="btn-ghost bg-surface-card text-sm"
          >
            <option>BTC/USDT</option>
            <option>ETH/USDT</option>
            <option>BNB/USDT</option>
          </select>
          <button type="button" onClick={runScan} className="btn-primary">
            Run Fraud Scan
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card md:col-span-1">
          <p className="text-gray-500 text-sm">Live Price</p>
          <p className="text-3xl font-bold text-accent mt-1 mono">
            ${price?.price?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
          <p className={`text-sm mt-1 ${(price?.change_24h || 0) >= 0 ? 'text-accent' : 'text-accent-danger'}`}>
            {(price?.change_24h || 0) >= 0 ? '+' : ''}{price?.change_24h?.toFixed(2)}% 24h
          </p>
          <p className="text-xs text-gray-600 mt-2">Source: {price?.source}</p>
        </div>
        <div className="card md:col-span-2">
          <h3 className="font-semibold mb-3">{symbol} — 24h Chart</h3>
          <PriceChart history={history} symbol={symbol} />
        </div>
        <div className="card flex flex-col items-center justify-center">
          <RiskMeter score={avgRisk} />
          <p className="text-xs text-gray-500 mt-2">Portfolio avg risk</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AlertsPanel alerts={alerts} liveAlert={liveAlert} />
        </div>
        <div className="card">
          <h3 className="font-semibold mb-4">Quick Stats</h3>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Active Alerts</dt>
              <dd className="font-mono text-accent-danger">{alerts.length}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Avg Risk Score</dt>
              <dd className="font-mono">{avgRisk.toFixed(1)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">24h Volume</dt>
              <dd className="font-mono text-xs">
                ${((price?.volume_24h || 0) / 1e6).toFixed(1)}M
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
