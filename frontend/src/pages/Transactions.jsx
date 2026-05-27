import { useEffect, useState } from 'react'
import { api } from '../services/api'

function riskBadge(level) {
  const styles = {
    high: 'bg-accent-danger/20 text-accent-danger border-accent-danger/40',
    medium: 'bg-accent-warn/20 text-accent-warn border-accent-warn/40',
    low: 'bg-accent/20 text-accent border-accent/40',
  }
  return styles[level] || styles.low
}

export default function Transactions() {
  const [txs, setTxs] = useState([])
  const [riskFilter, setRiskFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.transactions(100, riskFilter)
      setTxs(res.transactions || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [riskFilter])

  const exportCsv = () => {
    window.open(api.exportCsv(riskFilter), '_blank')
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Transactions</h2>
          <p className="text-gray-500 text-sm">ML-scored blockchain activity</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {['', 'high', 'medium', 'low'].map((r) => (
            <button
              key={r || 'all'}
              type="button"
              onClick={() => setRiskFilter(r)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                riskFilter === r
                  ? 'bg-accent/20 text-accent border border-accent/40'
                  : 'btn-ghost'
              }`}
            >
              {r ? r.charAt(0).toUpperCase() + r.slice(1) : 'All'}
            </button>
          ))}
          <button type="button" onClick={exportCsv} className="btn-primary text-sm">
            Export CSV
          </button>
          <button type="button" onClick={load} className="btn-ghost text-sm">
            Refresh
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        {loading ? (
          <p className="text-gray-500 py-8 text-center">Loading…</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-white/5">
                <th className="pb-3 pr-4">TX ID</th>
                <th className="pb-3 pr-4">From</th>
                <th className="pb-3 pr-4">Amount</th>
                <th className="pb-3 pr-4">Risk</th>
                <th className="pb-3 pr-4">Fraud %</th>
                <th className="pb-3">Explanation</th>
              </tr>
            </thead>
            <tbody>
              {txs.map((tx) => (
                <tr
                  key={tx.transaction_id}
                  className={`border-b border-white/5 transition-colors ${
                    tx.risk_level === 'high'
                      ? 'bg-accent-danger/5 hover:bg-accent-danger/10'
                      : 'hover:bg-surface-hover'
                  }`}
                >
                  <td className="py-3 pr-4 mono text-xs">{tx.transaction_id?.slice(0, 14)}…</td>
                  <td className="py-3 pr-4 mono text-xs text-gray-400">
                    {tx.wallet_from?.slice(0, 10)}…
                  </td>
                  <td className="py-3 pr-4 font-medium">
                    {tx.amount?.toLocaleString()} {tx.symbol}
                  </td>
                  <td className="py-3 pr-4">
                    <span className={`px-2 py-0.5 rounded border text-xs font-semibold ${riskBadge(tx.risk_level)}`}>
                      {tx.risk_score?.toFixed(0)} — {tx.risk_level}
                    </span>
                  </td>
                  <td className="py-3 pr-4 mono">
                    {((tx.fraud_probability || 0) * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 text-gray-400 text-xs max-w-xs truncate">
                    {tx.explanations?.[0] || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && txs.length === 0 && (
          <p className="text-center text-gray-500 py-8">No transactions found</p>
        )}
      </div>
    </div>
  )
}
