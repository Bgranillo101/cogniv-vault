import { useEffect } from 'react'
import { useAgentStore } from '../stores/agentStore'

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

type AgentEventType =
  | 'AGENT_START'
  | 'AGENT_SEARCH'
  | 'AGENT_SYNTHESIZE'
  | 'AGENT_VERIFY'
  | 'AGENT_RETRY'
  | 'AGENT_RESULT'
  | 'AGENT_ERROR'

interface AgentEvent {
  type: AgentEventType
  ts: string
  payload: Record<string, unknown>
}

export function useAgentSocket(jobId: string | null) {
  const { setPhase, setScore, setAnswer, setError } = useAgentStore()

  useEffect(() => {
    if (!jobId) return
    const ws = new WebSocket(`${WS_URL}/ws/query/${jobId}`)

    ws.onmessage = (e) => {
      const event = JSON.parse(e.data) as AgentEvent
      switch (event.type) {
        case 'AGENT_START':
          setPhase('searching')
          break
        case 'AGENT_SEARCH':
          setPhase('searching')
          break
        case 'AGENT_SYNTHESIZE':
          setPhase('synthesizing')
          break
        case 'AGENT_VERIFY':
          setPhase('verifying')
          if (typeof event.payload.score === 'number') setScore(event.payload.score)
          break
        case 'AGENT_RETRY':
          setPhase('retrying')
          break
        case 'AGENT_RESULT':
          setPhase('done')
          if (typeof event.payload.answer === 'string') setAnswer(event.payload.answer)
          break
        case 'AGENT_ERROR':
          setError(String(event.payload.message ?? 'unknown error'))
          break
      }
    }

    ws.onerror = () => setError('websocket error')

    return () => ws.close()
  }, [jobId, setPhase, setScore, setAnswer, setError])
}
