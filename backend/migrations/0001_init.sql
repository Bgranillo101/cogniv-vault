-- 0001_init.sql — Cogniv-Vault Phase 2 schema.
-- Mirrors docs/DATA_MODEL.md. Apply via Supabase SQL editor.

create extension if not exists vector;
create extension if not exists pgcrypto;

create table if not exists documents (
  id           uuid primary key default gen_random_uuid(),
  filename     text not null,
  byte_size    integer not null,
  page_count   integer,
  uploaded_at  timestamptz not null default now(),
  status       text not null default 'queued'
               check (status in ('queued', 'processing', 'ready', 'failed'))
);

create index if not exists documents_uploaded_at_idx
  on documents (uploaded_at desc);

create table if not exists chunks (
  id           uuid primary key default gen_random_uuid(),
  document_id  uuid not null references documents(id) on delete cascade,
  ordinal      integer not null,
  content      text not null,
  token_count  integer,
  embedding    vector(384) not null,
  created_at   timestamptz not null default now(),
  unique (document_id, ordinal)
);

create index if not exists chunks_embedding_ivfflat
  on chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists chunks_document_id_idx
  on chunks (document_id);
