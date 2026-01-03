interface SensorCardProps {
  title: string
  value: string
  unit: string
  icon: string
}

const SensorCard = ({ title, value, unit, icon }: SensorCardProps) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {value}
            <span className="text-sm font-normal text-gray-500 ml-1">{unit}</span>
          </p>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  )
}

export default SensorCard
