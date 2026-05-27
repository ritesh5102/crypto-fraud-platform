import { useEffect, useState } from 'react'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { api } from '../services/api'

const COLORS = ['#ff4757', '#ffa502', '#00d4aa']

export default function Analytics() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.analytics().then(setData).catch(console.error)
  }, [])

  if (!data) {
    return <p className="text-gray-500 animate-pulse">Loading analytics…</p>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Risk Analytics</h2>
        <p className="text-gray-500 text-sm mt-1">
          Fraud vs safe distribution · Risk score histogram
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <p className="text-gray-500 text-sm">Total Transactions</p>
          <p className="text-4xl font-bold text-accent mt-2">{data.total_transactions}</p>
        </div>
        <div className="card text-center">
          <p className="text-gray-500 text-sm">Average Risk Score</p>
          <p className="text-4xl font-bold mt-2">{data.avg_risk}</p>
        </div>
        <div className="card text-center">
          <p className="text-gray-500 text-sm">High Risk Count</p>
          <p className="text-4xl font-bold text-accent-danger mt-2">
            {data.fraud_vs_safe?.find((d) => d.name === 'High Risk')?.value || 0}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-4">Fraud vs Safe</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data.fraud_vs_safe}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, value }) => `${name}: ${value}`}
              >
                {data.fraud_vs_safe?.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #333' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.risk_distribution}>
              <XAxis dataKey="range" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip contentStyle={{ background: '#1a2332', border: '1px solid #333' }} />
              <Bar dataKey="count" fill="#00d4aa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-2">Model Stack</h3>
        <p className="text-sm text-gray-400">
          Random Forest + XGBoost ensemble · Isolation Forest anomaly detection ·
          NetworkX graph centrality & cluster analysis · ccxt live Binance feed
        </p>
      </div>
    </div>
  )
}
