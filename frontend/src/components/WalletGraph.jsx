/** SVG wallet connection graph */
export default function WalletGraph({ data }) {
  const nodes = data?.nodes || []
  const edges = data?.edges || []

  if (!nodes.length) {
    return <p className="text-gray-500 text-center py-12">No graph data yet</p>
  }

  const width = 700
  const height = 400
  const cx = width / 2
  const cy = height / 2
  const r = Math.min(width, height) * 0.38

  const positioned = nodes.map((n, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2
    return {
      ...n,
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    }
  })

  const posMap = Object.fromEntries(positioned.map((n) => [n.id, n]))

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
      {edges.map((e, i) => {
        const s = posMap[e.source]
        const t = posMap[e.target]
        if (!s || !t) return null
        const strokeW = Math.min(1 + e.count * 0.5, 4)
        return (
          <line
            key={i}
            x1={s.x}
            y1={s.y}
            x2={t.x}
            y2={t.y}
            stroke="rgba(0,212,170,0.25)"
            strokeWidth={strokeW}
          />
        )
      })}
      {positioned.map((n) => {
        const fill = n.risk > 0.5 ? '#ff4757' : n.risk > 0.25 ? '#ffa502' : '#00d4aa'
        return (
          <g key={n.id}>
            <circle cx={n.x} cy={n.y} r={8 + n.degree * 0.5} fill={fill} opacity={0.85} />
            <text
              x={n.x}
              y={n.y + 18}
              textAnchor="middle"
              fill="#9ca3af"
              fontSize="9"
              fontFamily="JetBrains Mono"
            >
              {n.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
