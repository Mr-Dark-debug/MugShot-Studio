from supabase import create_client, Client
from core.config import settings

_supabase_client: Client = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        # Use service role key if available for server-side operations
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
        _supabase_client = create_client(settings.SUPABASE_URL, supabase_key)
    return _supabase_client