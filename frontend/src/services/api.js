const API_BASE = import.meta.env.VITE_API_URL || ''

export async function fetchJSON(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}

export const api = {
  health: () => fetchJSON('/api/health'),
  livePrice: (s = 'BTC/USDT') => fetchJSON(`/api/live-price?symbol=${encodeURIComponent(s)}`),
  transactions: (limit = 50, risk = '') => {
    const q = new URLSearchParams({ limit })
    if (risk) q.set('risk', risk)
    return fetchJSON(`/api/transactions?${q}`)
  },
  analyzeBatch: (n = 5) => fetchJSON(`/api/analyze/batch?count=${n}`, { method: 'POST' }),
  fraudAlerts: (limit = 30) => fetchJSON(`/api/fraud-alerts?limit=${limit}`),
  graph: () => fetchJSON('/api/graph'),
  analytics: () => fetchJSON('/api/analytics'),
  exportCsv: (risk = '') => `${API_BASE}/api/export/csv${risk ? `?risk=${risk}` : ''}`,
}

export function createAlertWebSocket(onMessage) {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = import.meta.env.VITE_WS_HOST || `${proto}//${window.location.host}`
  const ws = new WebSocket(`${host}/ws/alerts`)
  ws.onmessage = (e) => { try { onMessage(JSON.parse(e.data)) } catch {} }
  ws.onopen = () => { ws._ping = setInterval(() => ws.readyState === 1 && ws.send('ping'), 30000) }
  ws.onclose = () => clearInterval(ws._ping)
  return ws
}
