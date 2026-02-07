import { useEffect, useState } from 'react'
import { Thermometer, Droplets, Gauge, Wind, Eye } from 'lucide-react'
import useWebSocket from '../hooks/useWebSocket'
import { sensorApi } from '../services/api'
import type { SensorReading, AirQualityLevel } from '../types/sensors'
import SensorCard from './SensorCard'
import Charts from './Charts'

const aqLevel = (score: number | undefined): AirQualityLevel | undefined => {
  if (score === undefined) return undefined
  if (score >= 80) return 'Excellent'
  if (score >= 60) return 'Good'
  if (score >= 40) return 'Moderate'
  if (score >= 20) return 'Poor'
  return 'Very Poor'
}

const Dashboard = () => {
  const { data: wsData, status: wsStatus } = useWebSocket()
  const [reading, setReading] = useState<SensorReading | null>(null)

  // Seed with REST on mount, then prefer WebSocket data
  useEffect(() => {
    sensorApi.getCurrentReadings().then((res) => setReading(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    if (wsData) setReading(wsData)
  }, [wsData])

  const bme = reading?.sensors?.bme680
  const dht = reading?.sensors?.dht22
  const motion = reading?.sensors?.motion

  // Prefer BME680 temp/humidity, fall back to DHT22
  const temp = bme?.temperature ?? dht?.temperature
  const hum = bme?.humidity ?? dht?.humidity

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center gap-3">
          <span
            className={`inline-block h-2.5 w-2.5 rounded-full ${
              wsStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'
            }`}
          />
          <span className="text-sm text-gray-500">
            {reading?.timestamp
              ? `Updated ${new Date(reading.timestamp).toLocaleTimeString()}`
              : 'Waiting for data...'}
          </span>
        </div>
      </div>

      {/* Sensor cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <SensorCard
          title="Temperature"
          value={temp !== undefined ? temp.toFixed(1) : null}
          unit="\u00b0C"
          icon={<Thermometer size={24} />}
        />
        <SensorCard
          title="Humidity"
          value={hum !== undefined ? hum.toFixed(1) : null}
          unit="%"
          icon={<Droplets size={24} />}
        />
        <SensorCard
          title="Pressure"
          value={bme?.pressure !== undefined ? bme.pressure.toFixed(0) : null}
          unit="hPa"
          icon={<Gauge size={24} />}
        />
        <SensorCard
          title="Air Quality"
          value={bme?.air_quality_score !== undefined ? bme.air_quality_score.toFixed(0) : null}
          unit="/100"
          icon={<Wind size={24} />}
          status={aqLevel(bme?.air_quality_score)}
        />
        <SensorCard
          title="Motion"
          value={motion ? (motion.motion_detected ? 'Detected' : 'Clear') : null}
          unit=""
          icon={<Eye size={24} />}
        />
      </div>

      {/* Charts */}
      <Charts />
    </div>
  )
}

export default Dashboard
