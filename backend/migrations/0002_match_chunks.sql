-- Phase 3 — pgvector cosine-similarity retrieval RPC.
-- Apply once per Supabase environment via the SQL editor.

create or replace function match_chunks(
  query_embedding vector(384),
  match_count int default 5,
  document_ids uuid[] default null
) returns table (
  chunk_id uuid,
  document_id uuid,
  ordinal int,
  content text,
  similarity float
)
language sql
stable
as $$
  select
    c.id as chunk_id,
    c.document_id,
    c.ordinal,
    c.content,
    1 - (c.embedding <=> query_embedding) as similarity
  from chunks c
  where document_ids is null or c.document_id = any(document_ids)
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
