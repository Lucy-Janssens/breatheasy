import axios from 'axios'
import type { SensorReading, SensorHealth, HistoryReading, ReadingStats } from '../types/sensors'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  },
)

export const sensorApi = {
  getCurrentReadings: () =>
    api.get<SensorReading>('/sensors/current'),

  getHealth: () =>
    api.get<SensorHealth>('/sensors/health'),
}

export const readingsApi = {
  getHistory: (params?: {
    sensor_type?: string
    metric?: string
    start_time?: string
    end_time?: string
    limit?: number
  }) =>
    api.get<HistoryReading[]>('/readings/history', { params }),

  getStats: (metric: string, timeframe: string = '24h') =>
    api.get<ReadingStats>('/readings/stats', { params: { metric, timeframe } }),
}

export default api
