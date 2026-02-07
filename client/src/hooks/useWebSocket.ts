import { useState, useEffect, useRef, useCallback } from 'react'
import type { SensorReading, WebSocketStatus } from '../types/sensors'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/sensors`
const RECONNECT_BASE_MS = 1000
const RECONNECT_MAX_MS = 30000

interface UseWebSocketReturn {
  data: SensorReading | null
  status: WebSocketStatus
}

const useWebSocket = (): UseWebSocketReturn => {
  const [data, setData] = useState<SensorReading | null>(null)
  const [status, setStatus] = useState<WebSocketStatus>('connecting')
  const wsRef = useRef<WebSocket | null>(null)
  const retryRef = useRef(0)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return

    setStatus('connecting')
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setStatus('connected')
      retryRef.current = 0
    }

    ws.onmessage = (event) => {
      try {
        const parsed: SensorReading = JSON.parse(event.data)
        setData(parsed)
      } catch {
        console.warn('Failed to parse WS message', event.data)
      }
    }

    ws.onerror = () => {
      setStatus('error')
    }

    ws.onclose = () => {
      setStatus('disconnected')
      wsRef.current = null

      // Exponential back-off reconnect
      const delay = Math.min(
        RECONNECT_BASE_MS * Math.pow(2, retryRef.current),
        RECONNECT_MAX_MS,
      )
      retryRef.current += 1
      timerRef.current = setTimeout(connect, delay)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, [connect])

  return { data, status }
}

export default useWebSocket
