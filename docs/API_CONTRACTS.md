# API Contracts

All REST endpoints are rooted at `/api/v1`. All request/response bodies are JSON unless stated otherwise. Errors follow a uniform envelope.

## Error envelope

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "detail": {}
  }
}
```

## REST

### `GET /healthz`

Liveness probe.

**200**
```json
{ "status": "ok" }
```

### `POST /documents`

Upload a PDF for ingestion. Multipart form:

| field | type | notes |
|-------|------|-------|
| `file` | `application/pdf` | required, max 25 MB |

**202**
```json
{
  "document_id": "uuid",
  "filename": "string",
  "status": "queued"
}
```

**4xx** — validation errors via the error envelope.

### `GET /documents`

List ingested documents.

**200**
```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "string",
      "uploaded_at": "ISO-8601",
      "chunk_count": 0
    }
  ]
}
```

### `POST /query`

Start an agentic query. Returns a job handle for the WebSocket stream.

**Request**
```json
{ "question": "string", "document_ids": ["uuid"] }
```
`document_ids` is optional; omitted means "search across all documents."

**202**
```json
{ "job_id": "uuid" }
```

## WebSocket — `/ws/query/{job_id}`

Server pushes newline-delimited JSON events. Each event has:

```json
{
  "type": "AGENT_START | AGENT_SEARCH | AGENT_SYNTHESIZE | AGENT_VERIFY | AGENT_RETRY | AGENT_RESULT | AGENT_ERROR",
  "ts": "ISO-8601",
  "payload": { }
}
```

The client does not send messages after connecting; the socket is server-push-only and closes after `AGENT_RESULT` or `AGENT_ERROR`.

### Event payloads

#### `AGENT_START`
```json
{ "question": "string", "document_ids": ["uuid"] }
```

#### `AGENT_SEARCH`
```json
{
  "agent": "librarian",
  "top_k": 5,
  "hits": [
    { "chunk_id": "uuid", "document_id": "uuid", "score": 0.91, "preview": "string" }
  ]
}
```

#### `AGENT_SYNTHESIZE`
```json
{
  "agent": "analyst",
  "draft": "string",
  "tokens_in": 0,
  "tokens_out": 0
}
```

#### `AGENT_VERIFY`
```json
{
  "agent": "auditor",
  "score": 0.0,
  "passed": true,
  "critique": "string"
}
```

#### `AGENT_RETRY`
Emitted only when `AGENT_VERIFY.passed == false` and retries remain.
```json
{
  "attempt": 2,
  "max_attempts": 3,
  "refined_query": "string",
  "reason": "string"
}
```

#### `AGENT_RESULT`
Terminal success event.
```json
{
  "answer": "string",
  "confidence": 0.0,
  "low_confidence": false,
  "citations": [
    { "chunk_id": "uuid", "document_id": "uuid", "snippet": "string" }
  ],
  "trace": {
    "attempts": 1,
    "final_score": 0.92,
    "duration_ms": 0
  }
}
```

#### `AGENT_ERROR`
Terminal failure event.
```json
{
  "code": "string",
  "message": "string",
  "stage": "librarian | analyst | auditor | graph"
}
```

## TypeScript types (normative)

```ts
export type AgentEventType =
  | "AGENT_START"
  | "AGENT_SEARCH"
  | "AGENT_SYNTHESIZE"
  | "AGENT_VERIFY"
  | "AGENT_RETRY"
  | "AGENT_RESULT"
  | "AGENT_ERROR";

export interface AgentEvent<T = unknown> {
  type: AgentEventType;
  ts: string;
  payload: T;
}
```
