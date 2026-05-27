import { useEffect, useState } from 'react'
import { api } from '../services/api'
import WalletGraph from '../components/WalletGraph'

export default function GraphView() {
  const [graph, setGraph] = useState({ nodes: [], edges: [], clusters: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.graph()
      .then(setGraph)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Wallet Graph Analysis</h2>
        <p className="text-gray-500 text-sm mt-1">
          NetworkX-powered graph · Suspicious cluster detection
        </p>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-4">Connection Map</h3>
        {loading ? (
          <p className="text-gray-500 text-center py-12">Building graph…</p>
        ) : (
          <WalletGraph data={graph} />
        )}
        <div className="flex gap-4 mt-4 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-accent" /> Low risk
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-accent-warn" /> Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-accent-danger" /> High risk
          </span>
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-4">Suspicious Clusters</h3>
        {graph.clusters?.length === 0 ? (
          <p className="text-gray-500 text-sm">No clusters detected yet</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {graph.clusters?.map((c, i) => (
              <div
                key={i}
                className="p-4 rounded-lg bg-surface-hover border border-white/5"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${
                    c.risk === 'high' ? 'bg-accent-danger/30 text-accent-danger' : 'bg-accent-warn/30'
                  }`}>
                    {c.risk} risk
                  </span>
                  <span className="text-sm text-gray-500">{c.size} wallets</span>
                </div>
                <p className="text-sm text-gray-400">
                  {c.edge_count} edges · ${c.total_flow?.toLocaleString()} total flow
                </p>
                <p className="text-xs mono text-gray-600 mt-2 truncate">
                  {c.wallets?.slice(0, 3).map((w) => w.slice(0, 10)).join(' → ')}…
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
