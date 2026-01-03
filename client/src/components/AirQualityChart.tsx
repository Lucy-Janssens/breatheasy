import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useReadingsHistory } from '../hooks/useReadings'

const AirQualityChart = () => {
  const { data: readings, isLoading } = useReadingsHistory(24)

  if (isLoading || !readings) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Air Quality Trends (24h)</h2>
        <div className="h-64 flex items-center justify-center text-gray-500">
          Loading chart data...
        </div>
      </div>
    )
  }

  // Transform readings into chart data
  const chartData = readings
    .filter(reading => ['pm25', 'co2', 'temperature', 'humidity'].includes(reading.sensor_type))
    .reduce((acc, reading) => {
      const timestamp = new Date(reading.timestamp).getTime()
      const existing = acc.find(item => item.timestamp === timestamp)
      if (existing) {
        existing[reading.sensor_type] = reading.value
      } else {
        acc.push({
          timestamp,
          time: new Date(reading.timestamp).toLocaleTimeString(),
          [reading.sensor_type]: reading.value
        })
      }
      return acc
    }, [] as any[])
    .sort((a, b) => a.timestamp - b.timestamp)

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Air Quality Trends (24h)</h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
            />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="pm25"
              stroke="#8884d8"
              strokeWidth={2}
              name="PM2.5 (µg/m³)"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="co2"
              stroke="#82ca9d"
              strokeWidth={2}
              name="CO₂ (ppm)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default AirQualityChart
