import { create } from 'zustand'

export type AgentPhase =
  | 'idle'
  | 'searching'
  | 'synthesizing'
  | 'verifying'
  | 'retrying'
  | 'done'
  | 'error'

export interface AgentState {
  phase: AgentPhase
  score: number | null
  answer: string | null
  error: string | null
  setPhase: (p: AgentPhase) => void
  setScore: (s: number) => void
  setAnswer: (a: string) => void
  setError: (e: string) => void
  reset: () => void
}

export const useAgentStore = create<AgentState>((set) => ({
  phase: 'idle',
  score: null,
  answer: null,
  error: null,
  setPhase: (phase) => set({ phase }),
  setScore: (score) => set({ score }),
  setAnswer: (answer) => set({ answer }),
  setError: (error) => set({ error, phase: 'error' }),
  reset: () => set({ phase: 'idle', score: null, answer: null, error: null }),
}))
