const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface QueryRequest {
  question: string
  document_ids?: string[]
}

export interface QueryResponse {
  job_id: string
}

export async function submitQuery(req: QueryRequest): Promise<QueryResponse> {
  const r = await fetch(`${API_URL}/api/v1/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!r.ok) throw new Error(`query failed: ${r.status}`)
  return r.json()
}

export async function listDocuments(): Promise<unknown> {
  const r = await fetch(`${API_URL}/api/v1/documents`)
  if (!r.ok) throw new Error(`list failed: ${r.status}`)
  return r.json()
}
