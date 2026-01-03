import { useQuery } from '@tanstack/react-query'
import { readingsApi } from '../services/api'

export const useLatestReadings = () => {
  return useQuery({
    queryKey: ['readings', 'latest'],
    queryFn: async () => {
      const response = await readingsApi.getLatestReadings()
      return response.data
    },
    refetchInterval: 10000, // Refetch every 10 seconds
  })
}

export const useReadingsHistory = (hours = 24) => {
  return useQuery({
    queryKey: ['readings', 'history', hours],
    queryFn: async () => {
      const response = await readingsApi.getReadingsHistory(hours)
      return response.data
    },
    refetchInterval: 60000, // Refetch every minute
  })
}

export const useSensorReadings = (sensorId: string, limit = 100) => {
  return useQuery({
    queryKey: ['readings', 'sensor', sensorId, limit],
    queryFn: async () => {
      const response = await readingsApi.getReadingsBySensor(sensorId, limit)
      return response.data
    },
    enabled: !!sensorId,
  })
}
