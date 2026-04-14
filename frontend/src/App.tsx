import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PhaserGame } from './game/PhaserGame'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-full flex-col items-center justify-center gap-4 p-6">
        <header className="w-full max-w-4xl">
          <h1 className="text-2xl font-semibold tracking-tight">Cogniv-Vault</h1>
          <p className="text-sm text-neutral-400">
            Phase 1 — arrow keys move the librarian. Full agent loop lands in Phase 3.
          </p>
        </header>
        <main className="w-full max-w-4xl">
          <PhaserGame />
        </main>
      </div>
    </QueryClientProvider>
  )
}
