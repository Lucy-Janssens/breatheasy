import { useSensorHealth } from '../hooks/useSensors'
import { useLatestReadings } from '../hooks/useReadings'
import { CheckCircle2, XCircle, Activity } from 'lucide-react'

const Sensors = () => {
  const { data: health, isLoading: healthLoading } = useSensorHealth()
  const { data: latest } = useLatestReadings()

  if (healthLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading sensors...</div>
      </div>
    )
  }

  const sensors = [
    {
      id: 'bme680',
      name: 'BME680 Environmental Sensor',
      description: 'Temperature, Humidity, Pressure, Air Quality',
      address: 'I2C 0x76',
      active: health?.bme680 ?? false,
      data: latest?.sensors?.bme680,
    },
    {
      id: 'dht22',
      name: 'DHT22 Backup Sensor',
      description: 'Temperature, Humidity (backup)',
      address: 'GPIO 17',
      active: health?.dht22 ?? false,
      data: latest?.sensors?.dht22,
    },
    {
      id: 'motion',
      name: 'PIR Motion Sensor',
      description: 'Motion detection for display wake',
      address: 'GPIO 4',
      active: health?.motion ?? false,
      data: latest?.sensors?.motion,
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Sensors</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Activity size={16} />
          Manager: {health?.manager_running ? 'Running' : 'Stopped'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sensors.map((sensor) => (
          <div key={sensor.id} className="bg-white p-6 rounded-xl shadow">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-800">{sensor.name}</h3>
              {sensor.active ? (
                <CheckCircle2 className="text-green-500" size={20} />
              ) : (
                <XCircle className="text-red-400" size={20} />
              )}
            </div>

            <p className="text-sm text-gray-500 mb-2">{sensor.description}</p>
            <p className="text-xs text-gray-400 mb-4">Address: {sensor.address}</p>

            {sensor.data && (
              <div className="border-t pt-3 space-y-1 text-sm text-gray-600">
                {Object.entries(sensor.data).map(([key, val]) => (
                  <div key={key} className="flex justify-between">
                    <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">
                      {typeof val === 'number' ? val.toFixed(1) : String(val)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Sensors
