export default function RiskMeter({ score = 0, size = 120 }) {
  const r = (size - 16) / 2, c = 2 * Math.PI * r
  const off = c - (score / 100) * c
  const color = score >= 70 ? '#ff4757' : score >= 40 ? '#ffa502' : '#00d4aa'
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#243044" strokeWidth="8" />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold" style={{ color }}>{Math.round(score)}</span>
        <span className="text-xs text-gray-500">Risk</span>
      </div>
    </div>
  )
}
