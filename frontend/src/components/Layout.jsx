import { NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../services/api'

const nav = [
  { to: '/', label: 'Dashboard', icon: '◉' },
  { to: '/transactions', label: 'Transactions', icon: '⇄' },
  { to: '/graph', label: 'Wallet Graph', icon: '◎' },
  { to: '/analytics', label: 'Risk Analytics', icon: '▤' },
]

export default function Layout({ children }) {
  const [online, setOnline] = useState(false)

  useEffect(() => {
    api.health().then(() => setOnline(true)).catch(() => setOnline(false))
  }, [])

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 border-r border-white/5 bg-surface/80 backdrop-blur-xl flex flex-col shrink-0">
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-2">
            <span className="text-2xl text-accent">◆</span>
            <div>
              <h1 className="font-bold text-lg leading-tight">FraudIntel</h1>
              <p className="text-xs text-gray-500">AI Crypto Platform</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {nav.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-accent/15 text-accent border border-accent/30'
                    : 'text-gray-400 hover:bg-surface-hover hover:text-white'
                }`
              }
            >
              <span className="text-lg">{icon}</span>
              <span className="font-medium">{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${online ? 'bg-accent animate-pulse' : 'bg-accent-danger'}`} />
            <span className="text-gray-500">{online ? 'API Connected' : 'API Offline'}</span>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <header className="sticky top-0 z-10 border-b border-white/5 bg-surface/60 backdrop-blur-xl px-8 py-4">
          <p className="text-sm text-gray-500">Real-time fraud intelligence · ML + Graph Analysis</p>
        </header>
        <div className="p-8 animate-fade-in">{children}</div>
      </main>
    </div>
  )
}
