"""Supabase client singleton."""
from functools import lru_cache
from supabase import create_client

from llm_tracker.config import SUPABASE_URL, SUPABASE_KEY


@lru_cache(maxsize=1)
def get_supabase_client():
    """Create and return a reusable Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)
