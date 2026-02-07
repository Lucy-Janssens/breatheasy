import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { readingsApi } from '../services/api'
import type { HistoryReading } from '../types/sensors'

type Timeframe = '1h' | '6h' | '24h' | '7d'

const hoursForTimeframe = (tf: Timeframe): number => {
  switch (tf) {
    case '1h':
      return 1
    case '6h':
      return 6
    case '24h':
      return 24
    case '7d':
      return 168
  }
}

const limitForTimeframe = (tf: Timeframe): number => {
  switch (tf) {
    case '1h':
      return 200
    case '6h':
      return 500
    case '24h':
      return 800
    case '7d':
      return 1000
  }
}

interface ChartRow {
  time: string
  timestamp: number
  temperature?: number
  humidity?: number
  air_quality_score?: number
  pressure?: number
}

const buildChartData = (readings: HistoryReading[]): ChartRow[] => {
  const buckets = new Map<number, ChartRow>()

  for (const r of readings) {
    const ts = new Date(r.timestamp).getTime()
    // Bucket to the nearest 30 s so overlapping metrics group together
    const key = Math.round(ts / 30000) * 30000

    if (!buckets.has(key)) {
      buckets.set(key, {
        time: new Date(key).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        timestamp: key,
      })
    }

    const row = buckets.get(key)!
    if (r.metric === 'temperature' && r.sensor_type === 'bme680') row.temperature = r.value
    if (r.metric === 'humidity' && r.sensor_type === 'bme680') row.humidity = r.value
    if (r.metric === 'air_quality_score') row.air_quality_score = r.value
    if (r.metric === 'pressure') row.pressure = r.value
  }

  return Array.from(buckets.values()).sort((a, b) => a.timestamp - b.timestamp)
}

const Charts = () => {
  const [timeframe, setTimeframe] = useState<Timeframe>('24h')

  const now = new Date()
  const start = new Date(now.getTime() - hoursForTimeframe(timeframe) * 3600_000)

  const { data: readings, isLoading } = useQuery({
    queryKey: ['history', timeframe],
    queryFn: async () => {
      const res = await readingsApi.getHistory({
        sensor_type: 'bme680',
        start_time: start.toISOString(),
        limit: limitForTimeframe(timeframe),
      })
      return res.data
    },
    refetchInterval: 60_000,
  })

  const chartData = readings ? buildChartData(readings) : []

  const timeframes: Timeframe[] = ['1h', '6h', '24h', '7d']

  return (
    <div className="space-y-6">
      {/* Time selector */}
      <div className="flex gap-2">
        {timeframes.map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              tf === timeframe
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tf}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="h-64 flex items-center justify-center text-gray-400">Loading chart data...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Temperature chart */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Temperature</h2>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                  <Tooltip />
                  <Line type="monotone" dataKey="temperature" stroke="#ef4444" strokeWidth={2} dot={false} name="Temp (\u00b0C)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Humidity chart */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Humidity</h2>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="humidity" stroke="#3b82f6" strokeWidth={2} dot={false} name="Humidity (%)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Air Quality chart */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Air Quality</h2>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="air_quality_score" stroke="#22c55e" strokeWidth={2} dot={false} name="AQ Score" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Pressure chart */}
          <div className="bg-white p-6 rounded-xl shadow">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Pressure</h2>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                  <Tooltip />
                  <Line type="monotone" dataKey="pressure" stroke="#a855f7" strokeWidth={2} dot={false} name="Pressure (hPa)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Charts
