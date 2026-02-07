import { useQuery } from '@tanstack/react-query'
import { sensorApi, readingsApi } from '../services/api'

export const useLatestReadings = () => {
  return useQuery({
    queryKey: ['readings', 'latest'],
    queryFn: async () => {
      const response = await sensorApi.getCurrentReadings()
      return response.data
    },
    refetchInterval: 10000,
  })
}

export const useReadingsHistory = (
  params?: { sensor_type?: string; metric?: string; limit?: number }
) => {
  return useQuery({
    queryKey: ['readings', 'history', params],
    queryFn: async () => {
      const response = await readingsApi.getHistory(params)
      return response.data
    },
    refetchInterval: 60000,
  })
}

export const useReadingStats = (metric: string, timeframe: string = '24h') => {
  return useQuery({
    queryKey: ['readings', 'stats', metric, timeframe],
    queryFn: async () => {
      const response = await readingsApi.getStats(metric, timeframe)
      return response.data
    },
    refetchInterval: 60000,
  })
}
