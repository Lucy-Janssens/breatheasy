import type { AirQualityLevel } from '../types/sensors'

interface SensorCardProps {
  title: string
  value: string | number | null
  unit: string
  icon: React.ReactNode
  status?: AirQualityLevel
}

const STATUS_COLORS: Record<AirQualityLevel, string> = {
  Excellent: 'bg-green-100 text-green-700',
  Good: 'bg-lime-100 text-lime-700',
  Moderate: 'bg-yellow-100 text-yellow-700',
  Poor: 'bg-orange-100 text-orange-700',
  'Very Poor': 'bg-red-100 text-red-700',
}

const SensorCard = ({ title, value, unit, icon, status }: SensorCardProps) => {
  const displayValue = value !== null && value !== undefined ? value : '--'

  return (
    <div className="bg-white p-6 rounded-xl shadow hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <div className="text-2xl text-gray-400">{icon}</div>
      </div>

      <p className="text-3xl font-bold text-gray-900">
        {displayValue}
        <span className="text-base font-normal text-gray-400 ml-1">{unit}</span>
      </p>

      {status && (
        <span
          className={`mt-3 inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${STATUS_COLORS[status]}`}
        >
          {status}
        </span>
      )}
    </div>
  )
}

export default SensorCard
