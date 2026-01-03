export const formatTemperature = (temp: number): string => {
  return `${temp.toFixed(1)}°C`
}

export const formatHumidity = (humidity: number): string => {
  return `${humidity.toFixed(1)}%`
}

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString()
}

export const formatRelativeTime = (timestamp: string): string => {
  const now = new Date()
  const time = new Date(timestamp)
  const diffInSeconds = Math.floor((now.getTime() - time.getTime()) / 1000)

  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

export const formatAirQuality = (value: number, type: string): string => {
  switch (type) {
    case 'pm25':
      return `${value.toFixed(1)} µg/m³`
    case 'pm10':
      return `${value.toFixed(1)} µg/m³`
    case 'co2':
      return `${Math.round(value)} ppm`
    case 'voc':
      return `${value.toFixed(1)} ppb`
    default:
      return value.toString()
  }
}
