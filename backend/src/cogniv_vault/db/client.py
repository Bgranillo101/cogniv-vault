"""Supabase client factory. Phase 2 wiring."""

from functools import lru_cache

from cogniv_vault.config import get_settings


@lru_cache(maxsize=1)
def get_supabase_client() -> object:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    from supabase import create_client

    return create_client(settings.supabase_url, settings.supabase_service_key)
