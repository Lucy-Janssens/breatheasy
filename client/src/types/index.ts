// Re-export everything from sensors for backward compatibility
export * from './sensors'

// Legacy types kept for existing components that import from here
export interface Sensor {
  id: string
  name: string
  type: string
  location: string
  is_active: boolean
  last_reading?: {
    value: number
    unit: string
    timestamp: string
  }
}

export interface AirQualityData {
  pm25: number
  pm10: number
  co2: number
  voc: number
  temperature: number
  humidity: number
  timestamp: string
}

export interface SystemStatus {
  uptime: number
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  last_update: string
}
