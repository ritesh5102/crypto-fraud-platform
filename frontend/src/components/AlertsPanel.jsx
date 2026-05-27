export default function AlertsPanel({ alerts = [], liveAlert = null }) {
  const all = liveAlert ? [liveAlert, ...alerts] : alerts
  const unique = all.filter(
    (a, i, arr) => arr.findIndex((x) => x.alert_id === a.alert_id || x.transaction_id === a.transaction_id) === i
  )

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg">Fraud Alerts</h3>
        <span className="text-xs px-2 py-1 rounded-full bg-accent-danger/20 text-accent-danger animate-pulse-slow">
          LIVE
        </span>
      </div>
      <div className="flex-1 overflow-y-auto space-y-3 max-h-80">
        {unique.length === 0 && (
          <p className="text-gray-500 text-sm text-center py-8">No alerts yet</p>
        )}
        {unique.slice(0, 15).map((alert) => (
          <div
            key={alert.alert_id || alert.transaction_id}
            className="p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/30 animate-fade-in"
          >
            <div className="flex justify-between items-start gap-2">
              <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${
                alert.risk_level === 'high' ? 'bg-accent-danger text-white' : 'bg-accent-warn/30 text-accent-warn'
              }`}>
                {alert.risk_level}
              </span>
              <span className="text-accent-danger font-mono font-bold">{alert.risk_score?.toFixed?.(0) ?? alert.risk_score}</span>
            </div>
            <p className="text-sm mt-2 text-gray-300">{alert.message}</p>
            <p className="text-xs text-gray-500 mt-1 mono">
              {alert.wallet_from?.slice(0, 12)}… · {alert.amount} {alert.symbol}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
