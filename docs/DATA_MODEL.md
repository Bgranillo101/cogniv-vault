# Data Model

Supabase Postgres with the `pgvector` extension. Two tables: `documents` and `chunks`.

## Extensions

```sql
create extension if not exists vector;
create extension if not exists pgcrypto;  -- gen_random_uuid()
```

## Tables

### `documents`

```sql
create table documents (
  id           uuid primary key default gen_random_uuid(),
  filename     text not null,
  byte_size    integer not null,
  page_count   integer,
  uploaded_at  timestamptz not null default now(),
  status       text not null default 'queued'
               check (status in ('queued', 'processing', 'ready', 'failed'))
);

create index on documents (uploaded_at desc);
```

### `chunks`

```sql
create table chunks (
  id           uuid primary key default gen_random_uuid(),
  document_id  uuid not null references documents(id) on delete cascade,
  ordinal      integer not null,
  content      text not null,
  token_count  integer,
  embedding    vector(384) not null,
  created_at   timestamptz not null default now(),
  unique (document_id, ordinal)
);

-- ivfflat index tuned for cosine similarity. `lists` ~ sqrt(rows); start at 100.
create index chunks_embedding_ivfflat
  on chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index on chunks (document_id);
```

## Embedding dimensions

`vector(384)` corresponds to `sentence-transformers/all-MiniLM-L6-v2`. See [DECISIONS/0003-embedding-model-minilm.md](DECISIONS/0003-embedding-model-minilm.md).

## Query pattern

```sql
select id, document_id, ordinal, content, 1 - (embedding <=> $1) as similarity
from chunks
where ($2::uuid[] is null or document_id = any($2))
order by embedding <=> $1
limit $3;
```

`<=>` is pgvector's cosine-distance operator; `1 - distance` yields similarity in `[0, 1]`.

## Index maintenance

- After bulk ingestion, run `analyze chunks;` to refresh planner stats.
- `lists` should be re-tuned (drop + recreate) once row counts exceed ~100k.

## Row-Level Security

RLS is not enabled in Phase 1 (single-tenant dev). Enable before any multi-tenant rollout.
