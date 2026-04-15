const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface QueryRequest {
  question: string
  document_ids?: string[]
}

export interface QuerySubmitResponse {
  job_id: string
}

export interface Citation {
  chunk_id: string
  document_id: string
  snippet: string
}

export interface QueryResult {
  answer: string
  confidence: number
  low_confidence: boolean
  citations: Citation[]
  trace: {
    attempts: number
    final_score: number
    duration_ms: number
  }
}

export async function submitQuery(req: QueryRequest): Promise<QuerySubmitResponse> {
  const r = await fetch(`${API_URL}/api/v1/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!r.ok) throw new Error(`query failed: ${r.status}`)
  return r.json()
}

export async function getQueryResult(jobId: string): Promise<QueryResult> {
  const r = await fetch(`${API_URL}/api/v1/query/${jobId}`)
  if (!r.ok) throw new Error(`result fetch failed: ${r.status}`)
  return r.json()
}

export async function listDocuments(): Promise<unknown> {
  const r = await fetch(`${API_URL}/api/v1/documents`)
  if (!r.ok) throw new Error(`list failed: ${r.status}`)
  return r.json()
}
