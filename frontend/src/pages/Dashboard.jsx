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

  const load = useCallback(async () => {
    const [p, a, an] = await Promise.all([api.livePrice(symbol), api.fraudAlerts(20), api.analytics()])
    setPrice(p.current)
    setHistory(p.history || [])
    setAlerts(a.alerts || [])
    setAvgRisk(an.avg_risk || 0)
  }, [symbol])

  useEffect(() => { load(); const t = setInterval(load, 30000); return () => clearInterval(t) }, [load])
  useEffect(() => {
    const ws = createAlertWebSocket(msg => {
      if (msg.type === 'fraud_alert' && msg.data) {
        setLiveAlert(msg.data)
        setAlerts(prev => [msg.data, ...prev].slice(0, 30))
      }
    })
    return () => ws.close()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center flex-wrap gap-4">
        <h2 className="text-2xl font-bold">Fraud Intelligence Dashboard</h2>
        <div className="flex gap-2">
          <select value={symbol} onChange={e => setSymbol(e.target.value)} className="btn-ghost bg-surface-card">
            <option>BTC/USDT</option><option>ETH/USDT</option><option>BNB/USDT</option>
          </select>
          <button type="button" className="btn-primary" onClick={async () => { await api.analyzeBatch(5); load() }}>Run Scan</button>
        </div>
      </div>
      <div className="grid md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-gray-500 text-sm">Live Price</p>
          <p className="text-2xl font-bold text-accent mono">${price?.price?.toLocaleString()}</p>
          <p className="text-sm">{price?.change_24h?.toFixed(2)}% 24h · {price?.source}</p>
        </div>
        <div className="card md:col-span-2"><PriceChart history={history} /></div>
        <div className="card flex justify-center"><RiskMeter score={avgRisk} /></div>
      </div>
      <AlertsPanel alerts={alerts} liveAlert={liveAlert} />
    </div>
  )
}
