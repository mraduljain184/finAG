import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart, ReferenceLine } from 'recharts'
import { Loader2 } from 'lucide-react'
import axios from 'axios'

function PriceChart({ ticker, currentPrice, support, resistance }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`/api/analyze/price-history/${ticker}?period=1y`)
        const { dates, close } = response.data.data

        const formatted = dates.map((date, i) => ({
          date,
          price: close[i],
        }))
        setData(formatted)
      } catch (err) {
        setError('Failed to load price history')
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [ticker])

  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <Loader2 className="animate-spin text-primary-500" size={24} />
      </div>
    )
  }

  if (error || data.length === 0) {
    return <p className="text-sm text-slate-500 text-center py-8">{error || 'No price data'}</p>
  }

  // Determine if trend is up or down to color the chart
  const firstPrice = data[0]?.price
  const lastPrice = data[data.length - 1]?.price
  const isUp = lastPrice >= firstPrice
  const chartColor = isUp ? '#16a34a' : '#dc2626'

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-sm text-slate-500">1-Year Price History</p>
          <p className="text-lg font-bold">
            ${firstPrice?.toFixed(2)} → ${lastPrice?.toFixed(2)}
            <span className={`ml-2 text-sm ${isUp ? 'text-green-600' : 'text-red-600'}`}>
              {isUp ? '+' : ''}{((lastPrice - firstPrice) / firstPrice * 100).toFixed(1)}%
            </span>
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={chartColor} stopOpacity={0.3} />
              <stop offset="100%" stopColor={chartColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#64748b' }}
            tickFormatter={(d) => {
              const [y, m] = d.split('-')
              return `${m}/${y.slice(2)}`
            }}
            interval={Math.floor(data.length / 6)}
            stroke="#cbd5e1"
          />
          <YAxis
            domain={['dataMin - 10', 'dataMax + 10']}
            tick={{ fontSize: 11, fill: '#64748b' }}
            tickFormatter={(v) => `$${v.toFixed(0)}`}
            stroke="#cbd5e1"
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '12px',
            }}
            formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          {support && <ReferenceLine y={support} stroke="#94a3b8" strokeDasharray="3 3" label={{ value: `Support $${support}`, position: 'insideBottomLeft', fontSize: 10, fill: '#64748b' }} />}
          {resistance && <ReferenceLine y={resistance} stroke="#94a3b8" strokeDasharray="3 3" label={{ value: `Resistance $${resistance}`, position: 'insideTopLeft', fontSize: 10, fill: '#64748b' }} />}
          <Area
            type="monotone"
            dataKey="price"
            stroke={chartColor}
            strokeWidth={2}
            fill="url(#colorPrice)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PriceChart