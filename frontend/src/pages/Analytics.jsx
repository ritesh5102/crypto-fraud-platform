import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { api } from '../services/api'

const COLORS = ['#ff4757', '#ffa502', '#00d4aa']

export default function Analytics() {
  const [data, setData] = useState(null)
  useEffect(() => { api.analytics().then(setData) }, [])
  if (!data) return <p className="text-gray-500">Loading…</p>
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Risk Analytics</h2>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="mb-4 font-semibold">Fraud vs Safe</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart><Pie data={data.fraud_vs_safe} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
              {data.fraud_vs_safe?.map((_, i) => <Cell key={i} fill={COLORS[i % 3]} />)}
            </Pie><Tooltip /><Legend /></PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3 className="mb-4 font-semibold">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.risk_distribution}><XAxis dataKey="range" stroke="#888" /><YAxis stroke="#888" />
              <Tooltip /><Bar dataKey="count" fill="#00d4aa" /></BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
