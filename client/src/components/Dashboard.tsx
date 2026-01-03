import { useLatestReadings } from '../hooks/useReadings'
import { formatTemperature, formatHumidity, formatAirQuality } from '../utils/formatters'
import AirQualityChart from './AirQualityChart'
import SensorCard from './SensorCard'

const Dashboard = () => {
  const { data: readings, isLoading, error } = useLatestReadings()

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-red-500">Error loading dashboard data</div>
      </div>
    )
  }

  // Group readings by sensor type for display
  const latestByType = readings?.reduce((acc, reading) => {
    if (!acc[reading.sensor_type] || new Date(reading.timestamp) > new Date(acc[reading.sensor_type].timestamp)) {
      acc[reading.sensor_type] = reading
    }
    return acc
  }, {} as Record<string, any>) || {}

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          Last updated: {readings?.[0] ? new Date(readings[0].timestamp).toLocaleTimeString() : 'Never'}
        </div>
      </div>

      {/* Current Readings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SensorCard
          title="Temperature"
          value={latestByType.temperature ? formatTemperature(latestByType.temperature.value) : '--'}
          unit="°C"
          icon="🌡️"
        />
        <SensorCard
          title="Humidity"
          value={latestByType.humidity ? formatHumidity(latestByType.humidity.value) : '--'}
          unit="%"
          icon="💧"
        />
        <SensorCard
          title="PM2.5"
          value={latestByType.pm25 ? formatAirQuality(latestByType.pm25.value, 'pm25') : '--'}
          unit="µg/m³"
          icon="🌫️"
        />
        <SensorCard
          title="CO₂"
          value={latestByType.co2 ? formatAirQuality(latestByType.co2.value, 'co2') : '--'}
          unit="ppm"
          icon="🌬️"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AirQualityChart />
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Air Quality Status</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>PM2.5:</span>
              <span className={latestByType.pm25?.value > 35 ? 'text-red-500' : latestByType.pm25?.value > 12 ? 'text-yellow-500' : 'text-green-500'}>
                {latestByType.pm25 ? (latestByType.pm25.value > 35 ? 'Poor' : latestByType.pm25.value > 12 ? 'Moderate' : 'Good') : 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>CO₂:</span>
              <span className={latestByType.co2?.value > 1000 ? 'text-red-500' : latestByType.co2?.value > 800 ? 'text-yellow-500' : 'text-green-500'}>
                {latestByType.co2 ? (latestByType.co2.value > 1000 ? 'Poor' : latestByType.co2.value > 800 ? 'Moderate' : 'Good') : 'Unknown'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
