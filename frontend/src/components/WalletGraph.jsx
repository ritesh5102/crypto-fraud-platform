export default function WalletGraph({ data }) {
  const nodes = data?.nodes || [], edges = data?.edges || []
  if (!nodes.length) return <p className="text-gray-500 text-center py-8">No graph data</p>
  const w = 600, h = 360, cx = w/2, cy = h/2, rad = 140
  const pos = nodes.map((n, i) => {
    const a = (2 * Math.PI * i) / nodes.length - Math.PI/2
    return { ...n, x: cx + rad * Math.cos(a), y: cy + rad * Math.sin(a) }
  })
  const map = Object.fromEntries(pos.map(n => [n.id, n]))
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
      {edges.map((e, i) => {
        const s = map[e.source], t = map[e.target]
        if (!s || !t) return null
        return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="rgba(0,212,170,0.3)" strokeWidth={2} />
      })}
      {pos.map(n => (
        <g key={n.id}>
          <circle cx={n.x} cy={n.y} r={8} fill={n.risk > 0.5 ? '#ff4757' : '#00d4aa'} />
          <text x={n.x} y={n.y+16} textAnchor="middle" fill="#888" fontSize="8">{n.label}</text>
        </g>
      ))}
    </svg>
  )
}
