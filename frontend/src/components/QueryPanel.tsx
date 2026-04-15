import { useState } from 'react'
import { getQueryResult, submitQuery, type QueryResult } from '../api/client'

export function QueryPanel() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<QueryResult | null>(null)

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!question.trim() || loading) return
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const { job_id } = await submitQuery({ question })
      const res = await getQueryResult(job_id)
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="w-full rounded border border-neutral-800 bg-neutral-950 p-4">
      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          className="flex-1 rounded border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-neutral-100 placeholder-neutral-500"
          placeholder="Ask your library a question…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-400">Error: {error}</p>}

      {result && (
        <div className="mt-4 space-y-3 text-sm">
          <div className="flex items-center gap-3 text-xs text-neutral-400">
            <span>confidence: {result.confidence.toFixed(2)}</span>
            <span>attempts: {result.trace.attempts}</span>
            <span>{result.trace.duration_ms} ms</span>
            {result.low_confidence && (
              <span className="rounded bg-amber-900/40 px-2 py-0.5 text-amber-300">
                low confidence
              </span>
            )}
          </div>
          <p className="whitespace-pre-wrap text-neutral-100">{result.answer}</p>
          {result.citations.length > 0 && (
            <details className="text-xs text-neutral-400">
              <summary className="cursor-pointer">
                {result.citations.length} citation{result.citations.length === 1 ? '' : 's'}
              </summary>
              <ul className="mt-2 space-y-2">
                {result.citations.map((c, i) => (
                  <li key={c.chunk_id} className="rounded border border-neutral-800 p-2">
                    <div className="text-neutral-500">
                      [{i + 1}] {c.document_id.slice(0, 8)}…
                    </div>
                    <div className="mt-1 text-neutral-300">{c.snippet}</div>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </section>
  )
}
