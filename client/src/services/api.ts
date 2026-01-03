import axios from 'axios'
import { SensorReading, Sensor, AirQualityData, SystemStatus } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const sensorsApi = {
  getAllSensors: () => api.get<Sensor[]>('/sensors'),
  getSensor: (id: string) => api.get<Sensor>(`/sensors/${id}`),
  updateSensor: (id: string, data: Partial<Sensor>) =>
    api.put<Sensor>(`/sensors/${id}`, data),
}

export const readingsApi = {
  getLatestReadings: () => api.get<SensorReading[]>('/readings/latest'),
  getReadingsBySensor: (sensorId: string, limit = 100) =>
    api.get<SensorReading[]>(`/readings/sensor/${sensorId}?limit=${limit}`),
  getReadingsHistory: (hours = 24) =>
    api.get<SensorReading[]>(`/readings/history?hours=${hours}`),
}

export const airQualityApi = {
  getCurrentData: () => api.get<AirQualityData>('/air-quality/current'),
  getHistoryData: (hours = 24) =>
    api.get<AirQualityData[]>(`/air-quality/history?hours=${hours}`),
}

export const systemApi = {
  getStatus: () => api.get<SystemStatus>('/system/status'),
  restart: () => api.post('/system/restart'),
}

export default api
