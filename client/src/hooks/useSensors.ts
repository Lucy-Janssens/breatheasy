import { useQuery } from '@tanstack/react-query'
import { sensorApi } from '../services/api'

export const useSensorHealth = () => {
  return useQuery({
    queryKey: ['sensors', 'health'],
    queryFn: async () => {
      const response = await sensorApi.getHealth()
      return response.data
    },
    refetchInterval: 30000,
  })
}
