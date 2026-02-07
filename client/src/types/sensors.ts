export interface BME680Data {
  temperature: number
  humidity: number
  pressure: number
  air_quality_score: number
}

export interface DHTData {
  temperature: number
  humidity: number
}

export interface MotionData {
  motion_detected: boolean
  time_since_motion: number
}

export interface SensorReading {
  timestamp: string
  sensors: {
    bme680?: BME680Data
    dht22?: DHTData
    motion?: MotionData
  }
}

export interface HistoryReading {
  id: number
  timestamp: string
  sensor_type: string
  metric: string
  value: number
  unit: string
}

export interface SensorHealth {
  bme680: boolean
  dht22: boolean
  motion: boolean
  manager_running: boolean
}

export interface ReadingStats {
  min: number | null
  max: number | null
  avg: number | null
  count: number
  timeframe: string
}

export type AirQualityLevel = 'Excellent' | 'Good' | 'Moderate' | 'Poor' | 'Very Poor'

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'
