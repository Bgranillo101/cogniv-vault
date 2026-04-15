import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { QueryPanel } from './components/QueryPanel'
import { PhaserGame } from './game/PhaserGame'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-full flex-col items-center gap-4 p-6">
        <header className="w-full max-w-4xl">
          <h1 className="text-2xl font-semibold tracking-tight">Cogniv-Vault</h1>
          <p className="text-sm text-neutral-400">
            Phase 3 — ask your library. Live agent event streaming lands in Phase 4.
          </p>
        </header>
        <main className="flex w-full max-w-4xl flex-col gap-4">
          <QueryPanel />
          <PhaserGame />
        </main>
      </div>
    </QueryClientProvider>
  )
}
