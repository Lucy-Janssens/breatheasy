import { useSensors } from '../hooks/useSensors'
import { formatRelativeTime } from '../utils/formatters'

const Sensors = () => {
  const { data: sensors, isLoading, error } = useSensors()

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading sensors...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-red-500">Error loading sensors</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Sensors</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sensors?.map((sensor) => (
          <div key={sensor.id} className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{sensor.name}</h3>
              <span className={`px-2 py-1 rounded-full text-xs ${
                sensor.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {sensor.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium">Type:</span> {sensor.type}</p>
              <p><span className="font-medium">Location:</span> {sensor.location}</p>
              {sensor.last_reading && (
                <p>
                  <span className="font-medium">Last Reading:</span>{' '}
                  {sensor.last_reading.value} {sensor.last_reading.unit}{' '}
                  ({formatRelativeTime(sensor.last_reading.timestamp)})
                </p>
              )}
            </div>
          </div>
        ))}

        {sensors?.length === 0 && (
          <div className="col-span-full text-center py-12 text-gray-500">
            No sensors configured yet.
          </div>
        )}
      </div>
    </div>
  )
}

export default Sensors
