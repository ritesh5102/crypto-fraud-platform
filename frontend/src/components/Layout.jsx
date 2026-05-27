import { NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../services/api'

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/transactions', label: 'Transactions' },
  { to: '/graph', label: 'Wallet Graph' },
  { to: '/analytics', label: 'Analytics' },
]

export default function Layout({ children }) {
  const [online, setOnline] = useState(false)
  useEffect(() => { api.health().then(() => setOnline(true)).catch(() => setOnline(false)) }, [])

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 border-r border-white/5 bg-surface p-4 flex flex-col">
        <h1 className="font-bold text-lg text-accent mb-6">FraudIntel</h1>
        <nav className="space-y-1 flex-1">
          {nav.map(({ to, label }) => (
            <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) =>
              `block px-3 py-2 rounded-lg ${isActive ? 'bg-accent/20 text-accent' : 'text-gray-400 hover:bg-surface-hover'}`
            }>{label}</NavLink>
          ))}
        </nav>
        <p className="text-xs text-gray-500">{online ? '● API online' : '○ API offline'}</p>
      </aside>
      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  )
}
