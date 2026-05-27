export default function AlertsPanel({ alerts = [], liveAlert = null }) {
  const all = liveAlert ? [liveAlert, ...alerts] : alerts
  return (
    <div className="card">
      <h3 className="font-semibold mb-3">Fraud Alerts <span className="text-xs text-accent-danger">LIVE</span></h3>
      <div className="space-y-2 max-h-72 overflow-y-auto">
        {all.length === 0 && <p className="text-gray-500 text-sm">No alerts</p>}
        {all.slice(0, 12).map((a, i) => (
          <div key={a.alert_id || i} className="p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/20 text-sm">
            <div className="flex justify-between">
              <span className="uppercase text-xs font-bold text-accent-danger">{a.risk_level}</span>
              <span className="mono font-bold">{a.risk_score}</span>
            </div>
            <p className="mt-1 text-gray-300">{a.message}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
