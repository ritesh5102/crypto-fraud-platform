import { useEffect, useState } from 'react'
import { api } from '../services/api'
import WalletGraph from '../components/WalletGraph'

export default function GraphView() {
  const [graph, setGraph] = useState({ nodes: [], edges: [], clusters: [] })
  useEffect(() => { api.graph().then(setGraph) }, [])
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Wallet Graph</h2>
      <div className="card"><WalletGraph data={graph} /></div>
      <div className="card">
        <h3 className="font-semibold mb-3">Suspicious Clusters</h3>
        {graph.clusters?.map((c, i) => (
          <div key={i} className="p-3 mb-2 rounded bg-surface-hover text-sm">
            {c.size} wallets · {c.risk} risk · ${c.total_flow?.toLocaleString()} flow
          </div>
        ))}
      </div>
    </div>
  )
}
