const API_BASE = import.meta.env.VITE_API_URL || '';

export async function fetchJSON(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  health: () => fetchJSON('/api/health'),
  livePrice: (symbol = 'BTC/USDT') => fetchJSON(`/api/live-price?symbol=${encodeURIComponent(symbol)}`),
  transactions: (limit = 50, risk = '') => {
    const q = new URLSearchParams({ limit });
    if (risk) q.set('risk', risk);
    return fetchJSON(`/api/transactions?${q}`);
  },
  analyze: (body) => fetchJSON('/api/analyze', { method: 'POST', body: JSON.stringify(body) }),
  analyzeBatch: (count = 5) => fetchJSON(`/api/analyze/batch?count=${count}`, { method: 'POST' }),
  fraudAlerts: (limit = 30) => fetchJSON(`/api/fraud-alerts?limit=${limit}`),
  graph: () => fetchJSON('/api/graph'),
  analytics: () => fetchJSON('/api/analytics'),
  exportCsv: (risk = '') => {
    const q = risk ? `?risk=${risk}` : '';
    return `${API_BASE}/api/export/csv${q}`;
  },
};

export function createAlertWebSocket(onMessage) {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = import.meta.env.VITE_WS_HOST || `${proto}//${window.location.hostname}:8000`;
  const ws = new WebSocket(`${host}/ws/alerts`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      /* ignore */
    }
  };

  ws.onopen = () => {
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send('ping');
    }, 30000);
    ws._pingInterval = ping;
  };

  ws.onclose = () => {
    if (ws._pingInterval) clearInterval(ws._pingInterval);
  };

  return ws;
}
