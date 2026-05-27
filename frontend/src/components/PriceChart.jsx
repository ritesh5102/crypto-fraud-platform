import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler)

export default function PriceChart({ history = [], symbol = 'BTC/USDT' }) {
  const labels = history.map((h) => {
    const d = new Date(h.time)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  const prices = history.map((h) => h.close)

  const data = {
    labels,
    datasets: [
      {
        label: symbol,
        data: prices,
        borderColor: '#00d4aa',
        backgroundColor: 'rgba(0, 212, 170, 0.1)',
        fill: true,
        tension: 0.35,
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#6b7280', maxTicksLimit: 8 },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#6b7280' },
      },
    },
  }

  return (
    <div className="h-64 w-full">
      <Line data={data} options={options} />
    </div>
  )
}
