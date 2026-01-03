import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sensorsApi } from '../services/api'
import { Sensor } from '../types'

export const useSensors = () => {
  return useQuery({
    queryKey: ['sensors'],
    queryFn: async () => {
      const response = await sensorsApi.getAllSensors()
      return response.data
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

export const useSensor = (id: string) => {
  return useQuery({
    queryKey: ['sensor', id],
    queryFn: async () => {
      const response = await sensorsApi.getSensor(id)
      return response.data
    },
    enabled: !!id,
  })
}

export const useUpdateSensor = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Sensor> }) =>
      sensorsApi.updateSensor(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sensors'] })
    },
  })
}
