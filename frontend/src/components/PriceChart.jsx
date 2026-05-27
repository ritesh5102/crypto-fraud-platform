import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler)

export default function PriceChart({ history = [] }) {
  const labels = history.map(h => new Date(h.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
  return (
    <div className="h-56">
      <Line data={{
        labels,
        datasets: [{ data: history.map(h => h.close), borderColor: '#00d4aa', backgroundColor: 'rgba(0,212,170,0.1)',
          fill: true, tension: 0.35, pointRadius: 0 }],
      }} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
        scales: { x: { ticks: { color: '#6b7280', maxTicksLimit: 8 }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#6b7280' }, grid: { color: 'rgba(255,255,255,0.05)' } } } }} />
    </div>
  )
}
