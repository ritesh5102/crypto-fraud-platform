import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function Transactions() {
  const [txs, setTxs] = useState([])
  const [risk, setRisk] = useState('')
  useEffect(() => { api.transactions(100, risk).then(r => setTxs(r.transactions || [])) }, [risk])

  return (
    <div className="space-y-4">
      <div className="flex justify-between flex-wrap gap-2">
        <h2 className="text-2xl font-bold">Transactions</h2>
        <div className="flex gap-2">
          {['', 'high', 'medium', 'low'].map(r => (
            <button key={r||'all'} type="button" onClick={() => setRisk(r)} className={risk===r?'btn-primary':'btn-ghost'}>
              {r || 'All'}
            </button>
          ))}
          <a href={api.exportCsv(risk)} className="btn-primary">Export CSV</a>
        </div>
      </div>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-gray-500 border-b border-white/5">
            <th className="text-left py-2">TX</th><th>Amount</th><th>Risk</th><th>Fraud %</th><th>Explanation</th>
          </tr></thead>
          <tbody>
            {txs.map(tx => (
              <tr key={tx.transaction_id} className={tx.risk_level==='high'?'bg-accent-danger/5':''}>
                <td className="py-2 mono text-xs">{tx.transaction_id?.slice(0,12)}…</td>
                <td>{tx.amount} {tx.symbol}</td>
                <td><span className={tx.risk_level==='high'?'text-accent-danger':'text-accent-warn'}>{tx.risk_score} {tx.risk_level}</span></td>
                <td className="mono">{((tx.fraud_probability||0)*100).toFixed(1)}%</td>
                <td className="text-gray-400 text-xs">{tx.explanations?.[0]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
